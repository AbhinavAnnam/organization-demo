import uuid
import datetime
from typing import List, Dict, Optional, Set, Any, Tuple
from dataclasses import dataclass, field

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None  # type: ignore


# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------

class AdminAuthorizationException(Exception):
    """Raised when an unauthenticated or unauthorized user attempts administrative actions."""
    pass


class DestructiveActionConfirmationRequiredException(Exception):
    """Raised when a destructive or high-privilege action lacks explicit confirmation."""
    pass


class InvalidOwnerAssignmentException(Exception):
    """Raised when an invalid account or non-member is assigned as organization owner."""
    pass


class OwnerNotFoundException(Exception):
    """Raised when an organization lacks a valid active owner."""
    pass


class ParentAccessDeniedException(Exception):
    """Raised when access to a parent container (project or work item) is denied."""
    pass


class ValidationError(Exception):
    """Raised when input data fails validation checks."""
    pass


class AuthorizationError(Exception):
    """Raised when user permissions are insufficient to access a resource."""
    pass


class InternalServerError(Exception):
    """Raised when an unexpected server-side error occurs without leaking implementation details."""
    pass


# ----------------------------------------------------------------------
# Data Models
# ----------------------------------------------------------------------

@dataclass
class OrganizationSettings:
    """Configures security, timezone, and operational settings for an organization."""
    timezone_str: str = "UTC"
    require_mfa: bool = False
    allow_guest_invites: bool = True
    session_timeout_minutes: int = 480

    def get_timezone(self) -> Any:
        if ZoneInfo is not None:
            try:
                return ZoneInfo(self.timezone_str)
            except Exception:
                pass
        return datetime.timezone.utc


@dataclass
class MemberInfo:
    """Represents a member within an organization with role and status information."""
    account_id: uuid.UUID
    email: str
    role: str  # 'owner', 'admin', 'member'
    is_active: bool = True
    joined_at: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))


@dataclass
class OrganizationContext:
    """Maintains tenant state, membership, settings, and metadata."""
    organization_id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    settings: OrganizationSettings = field(default_factory=OrganizationSettings)
    members: Dict[uuid.UUID, MemberInfo] = field(default_factory=dict)
    pending_invitations: Dict[str, Tuple[uuid.UUID, str]] = field(default_factory=dict)  # email -> (token_id, role)


# ----------------------------------------------------------------------
# Administration Service
# ----------------------------------------------------------------------

class AdministrationService:
    """
    Handles administration, ownership transfer, membership management, 
    data visibility verification, and paginated audit operations.
    """

    def __init__(self, org_context: OrganizationContext) -> None:
        self.context = org_context

    def verify_tenant_access(self, account_id: uuid.UUID) -> MemberInfo:
        """Verify that an account is an active member of the organization tenant."""
        member = self.context.members.get(account_id)
        if not member or not member.is_active:
            raise AuthorizationError("Access denied: user is not an active member of this organization.")
        return member

    def verify_admin_privileges(self, account_id: uuid.UUID) -> MemberInfo:
        """Verify that an account holds active administrator or owner privileges."""
        member = self.verify_tenant_access(account_id)
        if member.role not in ('owner', 'admin'):
            raise AdminAuthorizationException("Administrator privileges are required for this operation.")
        return member

    def verify_owner_privileges(self, account_id: uuid.UUID) -> MemberInfo:
        """Verify that an account holds active organization owner privileges."""
        member = self.verify_tenant_access(account_id)
        if member.role != 'owner':
            raise AdminAuthorizationException("Organization owner privileges are required for this operation.")
        return member

    def update_organization_settings(
        self,
        requester_id: uuid.UUID,
        new_settings: OrganizationSettings
    ) -> OrganizationSettings:
        """Update organization settings with strict administrative verification."""
        self.verify_admin_privileges(requester_id)
        self.context.settings = new_settings
        return self.context.settings

    def invite_member(
        self,
        requester_id: uuid.UUID,
        email: str,
        assigned_role: str = 'member',
        idempotency_key: Optional[str] = None
    ) -> str:
        """Invite a new member to the organization, supporting idempotent retries."""
        self.verify_admin_privileges(requester_id)
        if not email or "@" not in email:
            raise ValidationError("A valid email address is required for invitation.")
        
        if email in self.context.pending_invitations:
            token_uuid, _ = self.context.pending_invitations[email]
            return token_uuid.hex

        invitation_token = uuid.uuid4()
        self.context.pending_invitations[email] = (invitation_token, assigned_role)
        return invitation_token.hex

    def accept_invitation(
        self,
        account_id: uuid.UUID,
        email: str,
        invitation_token_str: str
    ) -> MemberInfo:
        """Accept an organization invitation and establish membership securely."""
        invitation_data = self.context.pending_invitations.get(email)
        if not invitation_data:
            raise AuthorizationError("Invalid or expired invitation.")

        token_uuid, assigned_role = invitation_data
        try:
            provided_token = uuid.UUID(invitation_token_str)
        except Exception as exc:
            raise ValidationError("Malformed invitation token format.") from exc

        if provided_token != token_uuid:
            raise AuthorizationError("Invalid invitation token.")

        member = MemberInfo(
            account_id=account_id,
            email=email,
            role=assigned_role,
            is_active=True,
            joined_at=datetime.datetime.now(datetime.timezone.utc)
        )
        self.context.members[account_id] = member
        del self.context.pending_invitations[email]
        return member

    def remove_member_from_organization(
        self,
        requester_id: uuid.UUID,
        target_account_id: uuid.UUID,
        confirmed: bool = False
    ) -> None:
        """Remove a member from the organization with explicit confirmation and safety checks."""
        self.verify_admin_privileges(requester_id)
        if not confirmed:
            raise DestructiveActionConfirmationRequiredException(
                "Destructive operations require explicit deliberate confirmation."
            )

        target_member = self.context.members.get(target_account_id)
        if not target_member:
            raise ValidationError("Target member does not exist in this organization.")

        if target_member.role == 'owner':
            raise InvalidOwnerAssignmentException("Cannot remove the organization owner.")

        del self.context.members[target_account_id]

    def transfer_ownership(
        self,
        requester_id: uuid.UUID,
        new_owner_id: uuid.UUID,
        confirmed: bool = False,
        new_previous_owner_role: str = 'admin'
    ) -> None:
        """Transfer organization ownership to an existing active member with strict validation and audit."""
        self.verify_owner_privileges(requester_id)
        if not confirmed:
            raise DestructiveActionConfirmationRequiredException(
                "Ownership transfer requires explicit deliberate confirmation."
            )

        new_owner = self.context.members.get(new_owner_id)
        if not new_owner or not new_owner.is_active:
            raise InvalidOwnerAssignmentException("New owner must be an active member of the organization.")

        current_owner = self.context.members.get(requester_id)
        if current_owner:
            self.context.members[requester_id] = MemberInfo(
                account_id=current_owner.account_id,
                email=current_owner.email,
                role=new_previous_owner_role,
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

    def recover_owner_emergency(
        self,
        emergency_admin_token: str,
        new_owner_id: uuid.UUID,
        expected_secret_hash: str
    ) -> None:
        """Emergency operational recovery procedure to prevent an organization from remaining ownerless."""
        if not emergency_admin_token or emergency_admin_token != expected_secret_hash:
            raise AdminAuthorizationException("Invalid emergency recovery credentials.")

        target_member = self.context.members.get(new_owner_id)
        if not target_member or not target_member.is_active:
            raise InvalidOwnerAssignmentException("Recovery owner must be an active organization member.")

        # Demote existing owners if any remain active
        for m_id, m_info in self.context.members.items():
            if m_info.role == 'owner' and m_id != new_owner_id:
                self.context.members[m_id] = MemberInfo(
                    account_id=m_info.account_id,
                    email=m_info.email,
                    role='admin',
                    is_active=m_info.is_active,
                    joined_at=m_info.joined_at
                )

        self.context.members[new_owner_id] = MemberInfo(
            account_id=target_member.account_id,
            email=target_member.email,
            role='owner',
            is_active=target_member.is_active,
            joined_at=target_member.joined_at
        )
        self.context.owner_id = new_owner_id

    def list_members_paginated(
        self,
        requester_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[MemberInfo]:
        """List organization members with stable pagination and administrative inspection rights."""
        self.verify_admin_privileges(requester_id)
        sorted_members = sorted(
            list(self.context.members.values()),
            key=lambda m: (m.joined_at, str(m.account_id))
        )
        return sorted_members[offset:offset + limit]

    def verify_data_visibility(
        self,
        requester_id: uuid.UUID,
        project_members_set: Set[uuid.UUID],
        is_project_private: bool = True
    ) -> None:
        """
        Enforce layered visibility: organization membership tenant boundary,
        project membership constraints, and inherited work item/comment/attachment rules.
        """
        self.verify_tenant_access(requester_id)
        
        # Check if requester is admin/owner
        member = self.context.members.get(requester_id)
        if member and member.role in ('owner', 'admin'):
            return

        if is_project_private and requester_id not in project_members_set:
            raise ParentAccessDeniedException("Access denied: user is not a member of the required project.")