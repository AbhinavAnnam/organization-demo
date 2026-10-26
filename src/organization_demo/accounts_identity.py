from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
import hashlib
import secrets
import threading
from typing import Optional, List, Dict, Set, Any


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class VerificationError(Exception):
    """Raised when email verification fails."""
    pass


class AccountNotFoundException(Exception):
    """Raised when an account is not found."""
    pass


class OrganizationAccessDeniedException(Exception):
    """Raised when organization access is denied."""
    pass


class InvitationExpiredException(Exception):
    """Raised when an invitation has expired or been revoked."""
    pass


class InvitationRevokedException(Exception):
    """Raised when an invitation has been revoked."""
    pass


class InvalidIdentifierException(Exception):
    """Raised when an identifier is invalid or conflicts."""
    pass


class InvalidOrganizationSettingException(Exception):
    """Raised when an organization setting value is invalid."""
    pass


class UnauthorizedSettingsUpdateException(Exception):
    """Raised when an unauthorized user attempts to update settings."""
    pass


class UnauthorizedAdminAccessException(Exception):
    """Raised when a non-admin attempts to access administration areas."""
    pass


class PrivilegeRevokedException(Exception):
    """Raised when admin or owner privileges have been revoked during a session."""
    pass


class UnauthorizedRoleElevationException(Exception):
    """Raised when a user attempts to elevate their own privileges."""
    pass


class OwnerRemovalException(Exception):
    """Raised when attempting to remove the owner without transfer."""
    pass


class InvalidOwnershipTransferException(Exception):
    """Raised when ownership transfer parameters are invalid."""
    pass


class MemberNotFoundException(Exception):
    """Raised when a member is not found in the organization."""
    pass


class UnauthorizedOwnershipTransferException(Exception):
    """Raised when a non-owner attempts to transfer ownership."""
    pass


class UnauthorizedException(Exception):
    """Raised when a user is unauthorized."""
    pass


class InvalidCredentialsException(Exception):
    """Raised when credentials are invalid."""
    pass


class VerificationRequiredException(Exception):
    """Raised when email verification is required."""
    pass


class OrganizationNotFoundException(Exception):
    """Raised when an organization is not found."""
    pass


class UnauthorizedAccessException(Exception):
    """Raised when access is unauthorized."""
    pass


class InsufficientPermissionsException(Exception):
    """Raised when permissions are insufficient."""
    pass


class UnverifiedAccountException(Exception):
    """Raised when an unverified account attempts restricted operations."""
    pass


class InvalidPasswordResetTokenException(Exception):
    """Raised when a password reset token is invalid or expired."""
    pass


class EmailAlreadyExistsException(Exception):
    """Raised when an email is already registered."""
    pass


class DuplicateOrganizationIdentifierException(Exception):
    """Raised when an organization identifier or slug already exists."""
    pass


class UnauthorizedOrganizationAccessException(Exception):
    """Raised when access to an organization is unauthorized."""
    pass


class SettingNotFoundException(Exception):
    """Raised when a requested organization setting is not found."""
    pass


class InvalidSettingValueException(Exception):
    """Raised when a setting value is invalid."""
    pass


class InsufficientPermissionException(Exception):
    """Raised when permissions are insufficient for the requested action."""
    pass


class SelfRoleElevationException(Exception):
    """Raised when a user attempts to elevate their own role."""
    pass


class ProjectNotFoundException(Exception):
    """Raised when a project is not found."""
    pass


class InvalidProjectOwnerTransferException(Exception):
    """Raised when transferring project ownership is invalid."""
    pass


class ProjectDeletionBlockedException(Exception):
    """Raised when project deletion is blocked."""
    pass


class NonOrganizationMemberProjectAddException(Exception):
    """Raised when attempting to add a non-organization member to a project."""
    pass


class ProjectMemberNotFoundException(Exception):
    """Raised when a project member is not found."""
    pass


class CannotRemoveLastProjectOwnerException(Exception):
    """Raised when attempting to remove the last project owner."""
    pass


@dataclass
class Account:
    """Represents a user account in the system."""
    account_id: str
    email: str
    password_hash: str
    display_name: str
    is_verified: bool = False
    verification_token: Optional[str] = None
    is_active: bool = True
    password_reset_token: Optional[str] = None
    password_reset_expires_at: Optional[datetime] = None


@dataclass
class Session:
    """Represents an active user session."""
    session_id: str
    account_id: str
    created_at: datetime
    is_valid: bool = True


@dataclass
class Invitation:
    """Represents an invitation to join an organization."""
    invitation_id: str
    organization_id: str
    email: str
    role: str
    expires_at: datetime
    is_revoked: bool = False


@dataclass
class Membership:
    """Represents a user's membership and role within an organization."""
    account_id: str
    organization_id: str
    role: str  # 'owner', 'administrator', 'member'
    is_active: bool = True


@dataclass
class ProjectMembership:
    """Represents a user's membership within a specific project."""
    project_id: str
    account_id: str
    organization_id: str
    role: str = "member"  # 'owner', 'member'
    is_active: bool = True


@dataclass
class AuditLog:
    """Represents an administrative or system audit log entry."""
    log_id: str
    organization_id: str
    actor_account_id: str
    action: str
    details: str
    timestamp: datetime


@dataclass
class OrganizationSettingValue:
    """Represents an organization setting with explicit user-set tracking."""
    value: str
    explicitly_set: bool = True


@dataclass
class Organization:
    """A named organization with settings and identity details."""
    organization_id: str
    name: str
    slug: Optional[str] = None
    timezone: str = "UTC"
    settings: Dict[str, OrganizationSettingValue] = field(default_factory=dict)


@dataclass
class Project:
    """Represents a project within an organization."""
    project_id: str
    organization_id: str
    name: str
    description: str
    creator_id: str
    status: str = "active"  # 'active', 'completed', 'archived'
    due_date: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AccountsIdentityDirectory:
    """Central manager for accounts, sessions, organizations, projects, memberships, and RBAC."""

    def __init__(self) -> None:
        self._accounts: Dict[str, Account] = {}  # account_id -> Account
        self._email_to_id: Dict[str, str] = {}  # lowercase email -> account_id
        self._sessions: Dict[str, Session] = {}  # session_id -> Session
        self._organizations: Dict[str, Organization] = {}  # organization_id -> Organization
        self._slug_to_org_id: Dict[str, str] = {}  # slug -> organization_id
        self._memberships: Dict[str, List[Membership]] = {}  # organization_id -> list[Membership]
        self._projects: Dict[str, Project] = {}  # project_id -> Project
        self._project_memberships: Dict[str, List[ProjectMembership]] = {}  # project_id -> list[ProjectMembership]
        self._invitations: Dict[str, Invitation] = {}  # invitation_id -> Invitation
        self._audit_logs: List[AuditLog] = []
        self._idempotency_records: Dict[str, Any] = {}
        self._lock = threading.Lock()

    def _hash_password(self, password: str) -> str:
        """Hash a password securely without storing raw text."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register_account(self, email: str, password: str, display_name: str, idempotency_key: Optional[str] = None) -> Account:
        """Register a new user account requiring email verification with idempotency support."""
        normalized_email = email.strip().lower()
        with self._lock:
            if idempotency_key and idempotency_key in self._idempotency_records:
                cached_account_id = self._idempotency_records[idempotency_key]
                if cached_account_id in self._accounts:
                    return self._accounts[cached_account_id]

            if normalized_email in self._email_to_id:
                raise EmailAlreadyExistsException("An account with this email already exists.")

            account_id = secrets.token_hex(8)
            verification_token = secrets.token_urlsafe(32)
            password_hash = self._hash_password(password)

            account = Account(
                account_id=account_id,
                email=normalized_email,
                password_hash=password_hash,
                display_name=display_name,
                is_verified=False,
                verification_token=verification_token,
                is_active=True
            )

            self._accounts[account_id] = account
            self._email_to_id[normalized_email] = account_id
            if idempotency_key:
                self._idempotency_records[idempotency_key] = account_id
            return account

    def verify_account(self, verification_token: str, idempotency_key: Optional[str] = None) -> Account:
        """Verify ownership of an account email address with idempotency support."""
        with self._lock:
            if idempotency_key and idempotency_key in self._idempotency_records:
                cached_account_id = self._idempotency_records[idempotency_key]
                if cached_account_id in self._accounts:
                    return self._accounts[cached_account_id]

            target_account = None
            for account in self._accounts.values():
                if account.verification_token == verification_token:
                    target_account = account
                    break

            if not target_account:
                raise VerificationError("Invalid or expired verification token.")

            target_account.is_verified = True
            target_account.verification_token = None
            if idempotency_key:
                self._idempotency_records[idempotency_key] = target_account.account_id
            return target_account

    def authenticate(self, email: str, password: str, idempotency_key: Optional[str] = None) -> Session:
        """Authenticate user and return a session token with idempotency support."""
        normalized_email = email.strip().lower()
        with self._lock:
            account_id = self._email_to_id.get(normalized_email)
            if not account_id:
                raise InvalidCredentialsException("Invalid email or password.")

            account = self._accounts[account_id]
            if not account.is_active:
                raise AuthenticationError("Account is deactivated.")

            if account.password_hash != self._hash_password(password):
                raise InvalidCredentialsException("Invalid email or password.")

            if not account.is_verified:
                raise UnverifiedAccountException("Email verification required.")

            if idempotency_key and idempotency_key in self._idempotency_records:
                cached_session_id = self._idempotency_records[idempotency_key]
                if cached_session_id in self._sessions:
                    existing_session = self._sessions[cached_session_id]
                    if existing_session.is_valid and existing_session.account_id == account_id:
                        return existing_session

            session_id = secrets.token_urlsafe(32)
            session = Session(
                session_id=session_id,
                account_id=account_id,
                created_at=datetime.now(timezone.utc),
                is_valid=True
            )
            self._sessions[session_id] = session
            if idempotency_key:
                self._idempotency_records[idempotency_key] = session_id
            return session

    def request_password_reset(self, email: str) -> Optional[str]:
        """Request a password reset token without disclosing account existence."""
        normalized_email = email.strip().lower()
        with self._lock:
            account_id = self._email_to_id.get(normalized_email)
            if not account_id:
                return None

            account = self._accounts[account_id]
            if not account.is_active:
                return None

            reset_token = secrets.token_urlsafe(32)
            account.password_reset_token = reset_token
            account.password_reset_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
            return reset_token

    def reset_password(self, reset_token: str, new_password: str) -> None:
        """Reset password using temporary single-use token and invalidate all active sessions for the account."""
        with self._lock:
            target_account = None
            for account in self._accounts.values():
                if account.password_reset_token == reset_token:
                    target_account = account
                    break

            if not target_account:
                raise InvalidPasswordResetTokenException("Invalid or expired password reset token.")

            if target_account.password_reset_expires_at and target_account.password_reset_expires_at < datetime.now(timezone.utc):
                raise InvalidPasswordResetTokenException("Password reset token has expired.")

            target_account.password_hash = self._hash_password(new_password)
            target_account.password_reset_token = None
            target_account.password_reset_expires_at = None

            for session in self._sessions.values():
                if session.account_id == target_account.account_id:
                    session.is_valid = False

    def change_password(self, session_id: str, old_password: str, new_password: str) -> None:
        """Change user password, invalidating all prior sessions upon completion."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_valid:
                raise UnauthorizedException("Invalid or expired session.")

            account = self._accounts[session.account_id]
            if account.password_hash != self._hash_password(old_password):
                raise InvalidCredentialsException("Incorrect current password.")

            account.password_hash = self._hash_password(new_password)

            for s in self._sessions.values():
                if s.account_id == account.account_id:
                    s.is_valid = False

    def update_profile(self, session_id: str, display_name: str) -> Account:
        """Update profile information such as display name."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_valid:
                raise UnauthorizedException("Invalid or expired session.")

            account = self._accounts[session.account_id]
            if not account.is_active:
                raise AuthenticationError("Account is deactivated.")

            account.display_name = display_name
            return account

    def deactivate_account(self, session_id: str) -> None:
        """Deactivate the user account, preserving historical references across organizations while revoking access."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_valid:
                raise UnauthorizedException("Invalid or expired session.")

            account = self._accounts[session.account_id]
            account.is_active = False

            for s in self._sessions.values():
                if s.account_id == account.account_id:
                    s.is_valid = False

            for org_id, memberships_list in self._memberships.items():
                for m in memberships_list:
                    if m.account_id == account.account_id:
                        m.is_active = False

            for proj_id, proj_mems in self._project_memberships.items():
                for pm in proj_mems:
                    if pm.account_id == account.account_id:
                        pm.is_active = False

    def create_organization(self, session_id: str, name: str, slug: Optional[str] = None, timezone_str: str = "UTC", idempotency_key: Optional[str] = None) -> Organization:
        """Create an organization where the creator becomes the initial owner with idempotency support."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_valid:
                raise UnauthorizedException("Invalid or expired session.")

            account = self._accounts[session.account_id]
            if not account.is_active:
                raise AuthenticationError("Account is deactivated.")

            if idempotency_key and idempotency_key in self._idempotency_records:
                cached_org_id = self._idempotency_records[idempotency_key]
                if cached_org_id in self._organizations:
                    return self._organizations[cached_org_id]

            if slug and slug in self._slug_to_org_id:
                raise DuplicateOrganizationIdentifierException("Organization slug must be unique.")

            org_id = secrets.token_hex(8)
            organization = Organization(
                organization_id=org_id,
                name=name,
                slug=slug,
                timezone=timezone_str,
                settings={}
            )

            self._organizations[org_id] = organization
            if slug:
                self._slug_to_org_id[slug] = org_id

            membership = Membership(
                account_id=account.account_id,
                organization_id=org_id,
                role="owner",
                is_active=True
            )
            self._memberships[org_id] = [membership]

            self._audit_logs.append(AuditLog(
                log_id=secrets.token_hex(6),
                organization_id=org_id,
                actor_account_id=account.account_id,
                action="CREATE_ORGANIZATION",
                details=f"Organization {name} created with owner {account.account_id}",
                timestamp=datetime.now(timezone.utc)
            ))

            if idempotency_key:
                self._idempotency_records[idempotency_key] = org_id

            return organization

    def _get_membership(self, organization_id: str, account_id: str) -> Optional[Membership]:
        """Retrieve active or inactive membership for a user in an organization."""
        memberships = self._memberships.get(organization_id, [])
        for m in memberships:
            if m.account_id == account_id:
                return m
        return None

    def invite_member(self, session_id: str, organization_id: str, email: str, role: str) -> Invitation:
        """Invite an individual by email address to an organization with idempotency for pending invitations."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_valid:
                raise UnauthorizedException("Invalid or expired session.")

            actor_membership = self._get_membership(organization_id, session.account_id)
            if not actor_membership or not actor_membership.is_active or actor_membership.role not in ("owner", "administrator"):
                raise InsufficientPermissionException("Insufficient permissions to invite members.")

            if role not in ("administrator", "member"):
                raise UnauthorizedRoleElevationException("Invalid role assigned during invitation.")

            normalized_email = email.strip().lower()
            now = datetime.now(timezone.utc)
            for inv in self._invitations.values():
                if (inv.organization_id == organization_id and
                        inv.email == normalized_email and
                        inv.role == role and
                        not inv.is_revoked and
                        inv.expires_at > now):
                    return inv

            invitation_id = secrets.token_hex(8)
            invitation = Invitation(
                invitation_id=invitation_id,
                organization_id=organization_id,
                email=normalized_email,
                role=role,
                expires_at=now + timedelta(days=7),
                is_revoked=False
            )

            self._invitations[invitation_id] = invitation
            return invitation

    def revoke_invitation(self, session_id: str, invitation_id: str) -> None:
        """Revoke a pending organization invitation."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_valid:
                raise UnauthorizedException("Invalid or expired session.")

            invitation = self._invitations.get(invitation_id)
            if not invitation:
                raise InvalidIdentifierException("Invitation not found.")

            actor_membership = self._get_membership(invitation.organization_id, session.account_id)
            if not actor_membership or not actor_membership.is_active or actor_membership.role not in ("owner", "administrator"):
                raise InsufficientPermissionException("Insufficient permissions to revoke invitations.")

            invitation.is_revoked = True

    def accept_invitation(self, session_id: str, invitation_id: str) -> Membership:
        """Accept an organization invitation, adding the user as a member without consuming invitations from other orgs."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_valid:
                raise UnauthorizedException("Invalid or expired session.")

            account = self._accounts[session.account_id]
            if not account.is_active:
                raise AuthenticationError("Account is deactivated.")

            invitation = self._invitations.get(invitation_id)
            if not invitation:
                raise InvitationExpiredException("Invitation is invalid.")
            if invitation.is_revoked:
                raise InvitationRevokedException("Invitation has been revoked.")

            if invitation.expires_at < datetime.now(timezone.utc):
                raise InvitationExpiredException("Invitation has expired.")

            if invitation.email.strip().lower() != account.email.strip().lower():
                raise UnauthorizedOrganizationAccessException("Invitation email does not match authenticated account.")

            org_id = invitation.organization_id
            if org_id not in self._memberships:
                self._memberships[org_id] = []

            existing_membership = self._get_membership(org_id, account.account_id)
            if existing_membership:
                if existing_membership.is_active:
                    invitation.is_revoked = True
                    return existing_membership
                else:
                    existing_membership.is_active = True
                    existing_membership.role = invitation.role
                    invitation.is_revoked = True
                    return existing_membership

            membership = Membership(
                account_id=account.account_id,
                organization_id=org_id,
                role=invitation.role,
                is_active=True
            )
            self._memberships[org_id].append(membership)
            invitation.is_revoked = True
            return membership

    def update_organization_settings(self, session_id: str, organization_id: str, name: Optional[str] = None, timezone_str: Optional[str] = None, settings: Optional[Dict[str, str]] = None) -> Organization:
        """Update organization workspace settings, scoping configuration to the organization."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_valid:
                raise UnauthorizedException("Invalid or expired session.")

            membership = self._get_membership(organization_id, session.account_id)
            if not membership or not membership.is_active:
                raise PrivilegeRevokedException("Membership or privileges revoked.")

            if membership.role not in ("owner", "administrator"):
                raise UnauthorizedSettingsUpdateException("Only owners and administrators can update settings.")

            organization = self._organizations.get(organization_id)
            if not organization:
                raise OrganizationNotFoundException("Organization not found.")

            details_parts = []
            if name is not None:
                organization.name = name
                details_parts.append(f"name changed to {name}")
            if timezone_str is not None:
                organization.timezone = timezone_str
                details_parts.append(f"timezone changed to {timezone_str}")
            if settings is not None:
                for k, v in settings.items():
                    organization.settings[k] = OrganizationSettingValue(value=v, explicitly_set=True)
                details_parts.append("settings updated")

            self._audit_logs.append(AuditLog(
                log_id=secrets.token_hex(6),
                organization_id=organization_id,
                actor_account_id=session.account_id,
                action="UPDATE_ORGANIZATION_SETTINGS",
                details=", ".join(details_parts),
                timestamp=datetime.now(timezone.utc)
            ))

            return organization

    def inspect_members(self, session_id: str, organization_id: str, limit: int = 50, offset: int = 0) -> List[Membership]:
        """Inspect current active members with pagination, enforcing administrative authorization."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_valid:
                raise UnauthorizedException("Invalid or expired session.")

            membership = self._get_membership(organization_id, session.account_id)
            if not membership or not membership.is_active:
                raise PrivilegeRevokedException("Privileges revoked or access denied.")

            if membership.role not in ("owner", "administrator"):
                raise UnauthorizedAdminAccessException("Administrator or owner privileges required.")

            active_members = [m for m in self._memberships.get(organization_id, []) if m.is_active]
            return active_members[offset:offset + limit]

    def list_organization_invitations(self, session_id: str, organization_id: str) -> List[Invitation]:
        """List pending invitations for an organization, distinguishing them from active members."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_valid:
                raise UnauthorizedException("Invalid or expired session.")

            membership = self._get_membership(organization_id, session.account_id)
            if not membership or not membership.is_active or membership.role not in ("owner", "administrator"):
                raise UnauthorizedAdminAccessException("Administrator or owner privileges required.")

            now = datetime.now(timezone.utc)
            return [inv for inv in self._invitations.values() if inv.organization_id == organization_id and not inv.is_revoked and inv.expires_at > now]

    def update_member_role(self, session_id: str, organization_id: str, target_account_id: str, new_role: str) -> Membership:
        """Update a member's role ensuring members cannot elevate their own permissions or modify owners."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_valid:
                raise UnauthorizedException("Invalid or expired session.")

            actor_membership = self._get_membership(organization_id, session.account_id)
            if not actor_membership or not actor_membership.is_active or actor_membership.role not in ("owner", "administrator"):
                raise InsufficientPermissionException("Insufficient permissions to modify member roles.")

            if session.account_id == target_account_id:
                raise SelfRoleElevationException("Users cannot modify their own roles.")

            if new_role not in ("owner", "administrator", "member"):
                raise InvalidSettingValueException("Invalid role specified.")

            target_membership = self._get_membership(organization_id, target_account_id)
            if not target_membership or not target_membership.is_active:
                raise MemberNotFoundException("Target member not found in organization.")

            if target_membership.role == "owner":
                raise InsufficientPermissionException("Cannot modify organization owner role directly.")

            if actor_membership.role == "administrator" and new_role == "owner":
                raise InsufficientPermissionException("Administrators cannot promote members to owner.")

            if actor_membership.role == "administrator" and target_membership.role == "administrator":
                raise InsufficientPermissionException("Administrators cannot modify other administrator roles.")

            target_membership.role = new_role

            self._audit_logs.append(AuditLog(
                log_id=secrets.token_hex(6),
                organization_id=organization_id,
                actor_account_id=session.account_id,
                action="UPDATE_MEMBER_ROLE",
                details=f"Updated role for account {target_account_id} to {new_role}",
                timestamp=datetime.now(timezone.utc)
            ))

            return target_membership

    def remove_member(self, session_id: str, organization_id: str, target_account_id: str) -> None:
        """Remove a member from an organization immediately revoking access while preserving audit history."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_valid:
                raise UnauthorizedException("Invalid or expired session.")

            actor_membership = self._get_membership(organization_id, session.account_id)
            if not actor_membership or not actor_membership.is_active:
                raise PrivilegeRevokedException("Privileges revoked.")

            if actor_membership.role not in ("owner", "administrator"):
                raise InsufficientPermissionException("Insufficient permissions to remove members.")

            target_membership = self._get_membership(organization_id, target_account_id)
            if not target_membership or not target_membership.is_active:
                raise MemberNotFoundException("Member not found in organization.")

            if target_membership.role == "owner":
                raise OwnerRemovalException("Cannot remove the organization owner directly without transfer.")

            if actor_membership.role == "administrator" and target_membership.role == "administrator":
                raise InsufficientPermissionException("Administrators cannot remove other administrators.")

            target_membership.is_active = False

            for proj_id, proj_mems in self._project_memberships.items():
                for pm in proj_mems:
                    if pm.account_id == target_account_id and pm.organization_id == organization_id:
                        pm.is_active = False

            self._audit_logs.append(AuditLog(
                log_id=secrets.token_hex(6),
                organization_id=organization_id,
                actor_account_id=session.account_id,
                action="REMOVE_MEMBER",
                details=f"Removed account {target_account_id} from organization",
                timestamp=datetime.now(timezone.utc)
            ))

    def create_project(self, session_id: str, organization_id: str, name: str, description: str, due_date: Optional[datetime] = None) -> Project:
        """Create a project within an organization where the creator becomes the initial project owner."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_valid:
                raise UnauthorizedException("Invalid or expired session.")

            membership = self._get_membership(organization_id, session.account_id)
            if not membership or not membership.is_active:
                raise UnauthorizedOrganizationAccessException("User is not an active member of this organization.")

            project_id = secrets.token_hex(8)
            now = datetime.now(timezone.utc)
            project = Project(
                project_id=project_id,
                organization_id=organization_id,
                name=name,
                description=description,
                creator_id=session.account_id,
                status="active",
                due_date=due_date,
                created_at=now,
                updated_at=now
            )
            self._projects[project_id] = project

            proj_membership = ProjectMembership(
                project_id=project_id,
                account_id=session.account_id,
                organization_id=organization_id,
                role="owner",
                is_active=True
            )
            self._project_memberships[project_id] = [proj_membership]

            self._audit_logs.append(AuditLog(
                log_id=secrets.token_hex(6),
                organization_id=organization_id,
                actor_account_id=session.account_id,
                action="CREATE_PROJECT",
                details=f"Project {name} created with owner {session.account_id}",
                timestamp=now
            ))

            return project

    def add_project_member(self, session_id: str, organization_id: str, project_id: str, target_account_id: str, role: str = "member") -> ProjectMembership:
        """Add an organization member to a project."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_valid:
                raise UnauthorizedException("Invalid or expired session.")

            actor_membership = self._get_membership(organization_id, session.account_id)
            if not actor_membership or not actor_membership.is_active:
                raise UnauthorizedOrganizationAccessException("Access denied.")

            project = self._projects.get(project_id)
            if not project or project.organization_id != organization_id:
                raise ProjectNotFoundException("Project not found.")

            actor_proj_mems = self._project_memberships.get(project_id, [])
            is_proj_owner = any(pm.account_id == session.account_id and pm.role == "owner" and pm.is_active for pm in actor_proj_mems)
            if actor_membership.role not in ("owner", "administrator") and not is_proj_owner:
                raise InsufficientPermissionException("Insufficient permissions to add project members.")

            target_org_membership = self._get_membership(organization_id, target_account_id)
            if not target_org_membership or not target_org_membership.is_active:
                raise NonOrganizationMemberProjectAddException("Target user is not an active member of the organization.")

            if project_id not in self._project_memberships:
                self._project_memberships[project_id] = []

            existing_pm = None
            for pm in self._project_memberships[project_id]:
                if pm.account_id == target_account_id:
                    existing_pm = pm
                    break

            if existing_pm:
                existing_pm.is_active = True
                existing_pm.role = role
                return existing_pm

            pm = ProjectMembership(
                project_id=project_id,
                account_id=target_account_id,
                organization_id=organization_id,
                role=role,
                is_active=True
            )
            self._project_memberships[project_id].append(pm)
            return pm

    def remove_project_member(self, session_id: str, organization_id: str, project_id: str, target_account_id: str) -> None:
        """Remove a member from a project without deleting historical work assignments."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_valid:
                raise UnauthorizedException("Invalid or expired session.")

            actor_membership = self._get_membership(organization_id, session.account_id)
            if not actor_membership or not actor_membership.is_active:
                raise UnauthorizedOrganizationAccessException("Access denied.")

            project = self._projects.get(project_id)
            if not project or project.organization_id != organization_id:
                raise ProjectNotFoundException("Project not found.")

            actor_proj_mems = self._project_memberships.get(project_id, [])
            is_proj_owner = any(pm.account_id == session.account_id and pm.role == "owner" and pm.is_active for pm in actor_proj_mems)
            if actor_membership.role not in ("owner", "administrator") and not is_proj_owner:
                raise InsufficientPermissionException("Insufficient permissions to remove project members.")

            target_pm = None
            for pm in actor_proj_mems:
                if pm.account_id == target_account_id and pm.is_active:
                    target_pm = pm
                    break

            if not target_pm:
                raise ProjectMemberNotFoundException("Project member not found.")

            if target_pm.role == "owner":
                active_owners = [pm for pm in actor_proj_mems if pm.role == "owner" and pm.is_active]
                if len(active_owners) <= 1:
                    raise CannotRemoveLastProjectOwnerException("Cannot remove the last project owner.")

            target_pm.is_active = False

    def archive_project(self, session_id: str, organization_id: str, project_id: str) -> Project:
        """Archive a project, removing it from active views while preserving inspectability."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_valid:
                raise UnauthorizedException("Invalid or expired session.")

            actor_membership = self._get_membership(organization_id, session.account_id)
            if not actor_membership or not actor_membership.is_active:
                raise UnauthorizedOrganizationAccessException("Access denied.")

            project = self._projects.get(project_id)
            if not project or project.organization_id != organization_id:
                raise ProjectNotFoundException("Project not found.")

            actor_proj_mems = self._project_memberships.get(project_id, [])
            is_proj_owner = any(pm.account_id == session.account_id and pm.role == "owner" and pm.is_active for pm in actor_proj_mems)
            if actor_membership.role not in ("owner", "administrator") and not is_proj_owner:
                raise InsufficientPermissionException("Insufficient permissions to archive project.")

            project.status = "archived"
            project.updated_at = datetime.now(timezone.utc)
            return project

    def delete_project(self, session_id: str, organization_id: str, project_id: str) -> None:
        """Permanently delete a project and clean up dependent memberships and records."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_valid:
                raise UnauthorizedException("Invalid or expired session.")

            actor_membership = self._get_membership(organization_id, session.account_id)
            if not actor_membership or not actor_membership.is_active:
                raise UnauthorizedOrganizationAccessException("Access denied.")

            project = self._projects.get(project_id)
            if not project or project.organization_id != organization_id:
                raise ProjectNotFoundException("Project not found.")

            if actor_membership.role not in ("owner", "administrator"):
                raise InsufficientPermissionException("Only organization owners and administrators can delete projects.")

            if project_id in self._projects:
                del self._projects[project_id]
            if project_id in self._project_memberships:
                del self._project_memberships[project_id]

    def transfer_ownership(self, session_id: str, organization_id: str, new_owner_account_id: str, previous_owner_new_role: str = "administrator") -> None:
        """Transfer organization ownership to another active member safely under lock."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_valid:
                raise UnauthorizedException("Invalid or expired session.")

            current_owner_membership = self._get_membership(organization_id, session.account_id)
            if not current_owner_membership or not current_owner_membership.is_active or current_owner_membership.role != "owner":
                raise UnauthorizedOwnershipTransferException("Only the current owner can transfer ownership.")

            if previous_owner_new_role not in ("administrator", "member"):
                raise InvalidOwnershipTransferException("Previous owner must become administrator or member.")

            recipient_membership = self._get_membership(organization_id, new_owner_account_id)
            if not recipient_membership or not recipient_membership.is_active:
                raise MemberNotFoundException("Ownership recipient must be an existing active member of the organization.")

            current_owner_membership.role = previous_owner_new_role
            recipient_membership.role = "owner"

            self._audit_logs.append(AuditLog(
                log_id=secrets.token_hex(6),
                organization_id=organization_id,
                actor_account_id=session.account_id,
                action="TRANSFER_OWNERSHIP",
                details=f"Ownership transferred from {session.account_id} to {new_owner_account_id}. Previous owner role set to {previous_owner_new_role}",
                timestamp=datetime.now(timezone.utc)
            ))

    def get_audit_logs(self, session_id: str, organization_id: str) -> List[AuditLog]:
        """Retrieve administrative audit logs for an organization."""
        with self._lock:
            session = self._sessions.get(session_id)
            if not session or not session.is_valid:
                raise UnauthorizedException("Invalid or expired session.")

            membership = self._get_membership(organization_id, session.account_id)
            if not membership or not membership.is_active or membership.role not in ("owner", "administrator"):
                raise UnauthorizedAdminAccessException("Admin privileges required to view audit logs.")

            return [log for log in self._audit_logs if log.organization_id == organization_id]