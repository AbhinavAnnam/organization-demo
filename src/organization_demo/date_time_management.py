import uuid
import datetime
from typing import List, Dict, Optional, Set, Any
from dataclasses import dataclass, field

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None  # type: ignore


class TimezoneError(Exception):
    """Raised when an invalid timezone or timezone conversion error occurs."""
    pass


class InvalidDueDateError(Exception):
    """Raised when a due date is invalid or improperly formatted."""
    pass


class AdminPermissionError(Exception):
    """Raised when a non-admin user attempts an administrative operation."""
    pass


class OwnershipTransferError(Exception):
    """Raised when an ownership transfer cannot be completed."""
    pass


class OrganizationAccessError(Exception):
    """Raised when a user lacks organization-level access."""
    pass


@dataclass
class OrganizationSettings:
    """Configures timezone and security controls for an organization."""
    timezone_str: str = "UTC"
    require_mfa: bool = False
    allow_guest_invites: bool = True
    session_timeout_minutes: int = 480

    def get_timezone(self) -> Any:
        """Retrieve the ZoneInfo object for the organization timezone."""
        if ZoneInfo is not None:
            try:
                return ZoneInfo(self.timezone_str)
            except Exception:
                pass
        return datetime.timezone.utc


@dataclass
class MemberInfo:
    """Represents a member within an organization with role and status details."""
    account_id: uuid.UUID
    email: str
    role: str  # 'owner', 'admin', 'member'
    is_active: bool = True
    joined_at: datetime.datetime = field(default_factory=lambda: datetime.now(datetime.timezone.utc))


@dataclass
class OrganizationContext:
    """Maintains organizational settings, members, and administrative controls."""
    organization_id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    settings: OrganizationSettings = field(default_factory=OrganizationSettings)
    members: Dict[uuid.UUID, MemberInfo] = field(default_factory=dict)
    pending_invitations: Dict[str, uuid.UUID] = field(default_factory=dict)  # email -> account_id


@dataclass(frozen=True)
class EventTimestamp:
    """Represents an unambiguous timezone-aware event instant."""
    moment: datetime.datetime

    def __post_init__(self) -> None:
        if self.moment.tzinfo is None:
            object.__setattr__(self, 'moment', self.moment.replace(tzinfo=datetime.timezone.utc))


@dataclass(frozen=True)
class WorkItemDueDate:
    """Represents a fixed calendar date for a work item due date, independent of timezones."""
    calendar_date: datetime.date

    def format_for_display(self, org_settings: OrganizationSettings, viewer_tz_str: Optional[str] = None) -> str:
        """Format the calendar date for display without shifting the date across timezones."""
        return self.calendar_date.isoformat()

    def get_relative_label(self, current_date: Optional[datetime.date] = None) -> str:
        """Compute relative date labels ('today', 'tomorrow', 'yesterday') dynamically."""
        if current_date is None:
            current_date = datetime.date.today()
        
        delta = (self.calendar_date - current_date).days
        if delta == 0:
            return "today"
        elif delta == 1:
            return "tomorrow"
        elif delta == -1:
            return "yesterday"
        elif delta > 1:
            return f"in {delta} days"
        else:
            return f"{abs(delta)} days ago"


class DateTimeManagementService:
    """Manages organization timezone settings, unambiguous event timestamps, and calendar-bound due dates."""

    @staticmethod
    def create_event_timestamp(dt: datetime.datetime) -> datetime.datetime:
        """Ensure an event timestamp carries an unambiguous timezone representation (defaulting to UTC)."""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=datetime.timezone.utc)
        return dt.astimezone(datetime.timezone.utc)

    @staticmethod
    def adjust_for_dst(dt: datetime.datetime, target_timezone_str: str) -> datetime.datetime:
        """Adjust datetime for daylight-saving transitions without assuming fixed 24-hour day durations."""
        if ZoneInfo is not None:
            try:
                tz = ZoneInfo(target_timezone_str)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=datetime.timezone.utc)
                return dt.astimezone(tz)
            except Exception as e:
                raise TimezoneError(f"Invalid timezone: {target_timezone_str}") from e
        return dt.astimezone(datetime.timezone.utc)

    @staticmethod
    def parse_work_item_due_date(date_input: str | datetime.date) -> WorkItemDueDate:
        """Parse work item due date ensuring it represents a fixed calendar day unaffected by timezones."""
        if isinstance(date_input, datetime.date) and not isinstance(date_input, datetime.datetime):
            return WorkItemDueDate(calendar_date=date_input)
        elif isinstance(date_input, str):
            parsed_date = datetime.date.fromisoformat(date_input)
            return WorkItemDueDate(calendar_date=parsed_date)
        elif isinstance(date_input, datetime.datetime):
            return WorkItemDueDate(calendar_date=date_input.date())
        raise InvalidDueDateError(f"Cannot parse due date from {date_input}")


class AdministrationService:
    """Provides organization-level controls for membership management, pending invitations, and settings."""

    def __init__(self, org_context: OrganizationContext) -> None:
        self.context = org_context

    def verify_admin_privileges(self, account_id: uuid.UUID) -> None:
        """Verify that an account holds active administrator or owner privileges."""
        member = self.context.members.get(account_id)
        if not member or not member.is_active or member.role not in ('owner', 'admin'):
            raise AdminPermissionError("Administrator privileges are required for this operation.")

    def verify_owner_privileges(self, account_id: uuid.UUID) -> None:
        """Verify that an account holds active organization owner privileges."""
        member = self.context.members.get(account_id)
        if not member or not member.is_active or member.role != 'owner':
            raise OwnershipTransferError("Organization owner privileges are required for this operation.")

    def update_organization_settings(self, requester_id: uuid.UUID, new_settings: OrganizationSettings) -> OrganizationSettings:
        """Update organization settings with administrative permission checks."""
        self.verify_admin_privileges(requester_id)
        self.context.settings = new_settings
        return self.context.settings

    def invite_member(self, requester_id: uuid.UUID, email: str, assigned_role: str = 'member') -> str:
        """Invite a new member to the organization."""
        self.verify_admin_privileges(requester_id)
        invitation_token = uuid.uuid4().hex
        self.context.pending_invitations[email] = uuid.UUID(invitation_token[:32], hex=True)
        return invitation_token

    def accept_invitation(self, account_id: uuid.UUID, email: str, invitation_token: str) -> MemberInfo:
        """Accept an invitation to join the organization."""
        token_uuid = self.context.pending_invitations.get(email)
        if not token_uuid:
            raise OrganizationAccessError("Invalid or expired invitation.")
        
        member = MemberInfo(
            account_id=account_id,
            email=email,
            role='member',
            is_active=True,
            joined_at=datetime.datetime.now(datetime.timezone.utc)
        )
        self.context.members[account_id] = member
        del self.context.pending_invitations[email]
        return member

    def remove_member_from_organization(self, requester_id: uuid.UUID, target_account_id: uuid.UUID, confirmed: bool = False) -> None:
        """Remove a member from the organization with explicit confirmation and admin checks."""
        self.verify_admin_privileges(requester_id)
        if not confirmed:
            raise AdminPermissionError("Destructive operations require explicit deliberate confirmation.")
        
        target_member = self.context.members.get(target_account_id)
        if target_member and target_member.role == 'owner':
            raise OwnershipTransferError("Cannot remove the organization owner.")
        
        if target_account_id in self.context.members:
            del self.context.members[target_account_id]

    def transfer_ownership(self, requester_id: uuid.UUID, new_owner_id: uuid.UUID, confirmed: bool = False) -> None:
        """Transfer organization ownership with explicit confirmation and owner validation."""
        self.verify_owner_privileges(requester_id)
        if not confirmed:
            raise OwnershipTransferError("Ownership transfer requires explicit deliberate confirmation.")
        
        new_owner = self.context.members.get(new_owner_id)
        if not new_owner or not new_owner.is_active:
            raise OwnershipTransferError("New owner must be an active organization member.")

        current_owner = self.context.members.get(requester_id)
        if current_owner:
            self.context.members[requester_id] = MemberInfo(
                account_id=current_owner.account_id,
                email=current_owner.email,
                role='admin',
                is_active=current_owner.is_active,
                joined_at=current_owner.joined_at
            )

        self.context.members[new_owner_id] = MemberInfo(
            account_id=new_owner.account_id,
            email=new_owner.email,
            role='owner',
            is_active=new_owner.is_active,
            joined_at=new_owner.joined_at
        )
        self.context.owner_id = new_owner_id