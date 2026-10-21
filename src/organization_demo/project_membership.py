from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any, Optional
from zoneinfo import ZoneInfo


class ProjectNotFoundException(Exception):
    """Raised when a specified project cannot be found."""
    pass


class OrphanedDataException(Exception):
    """Raised when data integrity issues arise regarding orphaned records."""
    pass


class ProjectOwnerRequiredException(Exception):
    """Raised when an operation would leave a project without a designated owner."""
    pass


class AccessRevokedException(Exception):
    """Raised when access to a resource has been revoked."""
    pass


class InvalidStateTransitionException(Exception):
    """Raised when an invalid state transition is attempted on a work item or project."""
    pass


class MalformedWorkItemException(Exception):
    """Raised when a work item payload or structure is malformed."""
    pass


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class UnauthorizedObjectAccessException(Exception):
    """Raised when access is attempted on an object belonging to another organization or without permission."""
    pass


class ConcurrentModificationException(Exception):
    """Raised when a stale client view attempts to overwrite newer changes."""
    pass


@dataclass(frozen=True)
class Organization:
    """A named organization."""
    name: str


class OrganizationDirectory:
    """Store organizations in memory and return them in creation order."""

    def __init__(self) -> None:
        self._organizations: list[Organization] = []

    def create_organization(self, name: str) -> Organization:
        """Create and store an organization with the supplied name."""
        organization = Organization(name=name)
        self._organizations.append(organization)
        return organization

    def list_organizations(self) -> list[Organization]:
        """Return a snapshot of organizations in creation order."""
        return list(self._organizations)


@dataclass
class ProjectMember:
    """Represents a member within a project scope."""
    user_id: str
    is_owner: bool = False


@dataclass
class WorkItem:
    """Represents a work item belonging to a project."""
    id: str
    title: str
    status: str = "not_yet_completed"
    priority: str = "medium"
    assignee_id: Optional[str] = None
    due_date: Optional[date] = None
    description: str = ""
    position: int = 0
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    history: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Project:
    """Represents a body of related work with members, work items, and status."""
    id: str
    organization_name: str
    name: str
    creator_id: str
    owner_id: str
    description: str = ""
    status: str = "active"
    due_date: Optional[date] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    members: dict[str, ProjectMember] = field(default_factory=dict)
    work_items: dict[str, WorkItem] = field(default_factory=dict)
    activity_records: list[dict[str, Any]] = field(default_factory=list)
    comments: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    attachments: dict[str, list[dict[str, Any]]] = field(default_factory=dict)


class ProjectMembershipManager:
    """Manages projects, project memberships, work items, and project editing."""

    def __init__(self) -> None:
        self._projects: dict[str, Project] = {}

    def _sanitize_description(self, description: str) -> str:
        """Sanitize project descriptions to prevent XSS and executable content."""
        if not isinstance(description, str):
            return ""
        escaped = (
            description.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
        )
        return escaped

    def _get_utc_now(self, timezone_str: str = "UTC") -> datetime:
        """Return timezone-aware current time accounting for daylight saving shifts using zoneinfo."""
        try:
            tz = ZoneInfo(timezone_str)
        except Exception:
            tz = timezone.utc
        return datetime.now(tz)

    def create_project(
        self,
        project_id: str,
        organization_name: str,
        name: str,
        creator_id: str,
        owner_id: str,
        description: str = "",
        due_date: Optional[date] = None,
        timezone_str: str = "UTC",
    ) -> Project:
        """Create a new project within an organization."""
        if not project_id or not organization_name or not name or not creator_id or not owner_id:
            raise ValidationError("Project ID, organization name, name, creator ID, and owner ID are required.")
        
        sanitized_description = self._sanitize_description(description)
        now_dt = self._get_utc_now(timezone_str)
        
        members = {
            owner_id: ProjectMember(user_id=owner_id, is_owner=True)
        }
        if creator_id != owner_id:
            members[creator_id] = ProjectMember(user_id=creator_id, is_owner=False)

        project = Project(
            id=project_id,
            organization_name=organization_name,
            name=name,
            creator_id=creator_id,
            owner_id=owner_id,
            description=sanitized_description,
            due_date=due_date,
            created_at=now_dt,
            updated_at=now_dt,
            members=members
        )
        self._projects[project_id] = project
        return project

    def get_project(self, project_id: str, organization_name: str) -> Project:
        """Retrieve a project by ID and verify organization tenant isolation."""
        if not project_id:
            raise MalformedWorkItemException("Project ID is malformed or missing.")
        if project_id not in self._projects:
            raise ProjectNotFoundException(f"Project with ID '{project_id}' not found.")
        project = self._projects[project_id]
        if project.organization_name != organization_name:
            raise UnauthorizedObjectAccessException("Project belongs to another organization.")
        return project

    def add_project_member(
        self,
        project_id: str,
        organization_name: str,
        actor_id: str,
        user_id: str,
        is_owner: bool = False,
        org_members: Optional[list[str]] = None,
        timezone_str: str = "UTC",
    ) -> ProjectMember:
        """Add a member to a project. Enforces project ownership permissions and organization membership."""
        project = self.get_project(project_id, organization_name)
        
        if actor_id not in project.members or not project.members[actor_id].is_owner:
            raise UnauthorizedObjectAccessException("Only project owners can add members.")

        if org_members is not None and user_id not in org_members:
            raise ValidationError("Persons outside the organization cannot be added directly to a project.")

        if user_id in project.members:
            return project.members[user_id]

        member = ProjectMember(user_id=user_id, is_owner=is_owner)
        project.members[user_id] = member
        project.updated_at = self._get_utc_now(timezone_str)
        return member

    def remove_project_member(
        self,
        project_id: str,
        organization_name: str,
        actor_id: str,
        user_id: str,
        timezone_str: str = "UTC",
    ) -> None:
        """Remove a member from a project, ensuring owners cannot be removed without another owner."""
        project = self.get_project(project_id, organization_name)

        if actor_id not in project.members or not project.members[actor_id].is_owner:
            raise UnauthorizedObjectAccessException("Only project owners can remove members.")

        if user_id not in project.members:
            raise ValidationError("User is not a member of this project.")

        target_member = project.members[user_id]
        if target_member.is_owner:
            owner_count = sum(1 for m in project.members.values() if m.is_owner)
            if owner_count <= 1:
                raise ProjectOwnerRequiredException("Cannot remove the last project owner without designating another owner.")

        del project.members[user_id]
        project.updated_at = self._get_utc_now(timezone_str)

    def archive_project(self, project_id: str, organization_name: str, actor_id: str, timezone_str: str = "UTC") -> Project:
        """Archive a project rather than permanently deleting it."""
        project = self.get_project(project_id, organization_name)
        if actor_id not in project.members or not project.members[actor_id].is_owner:
            raise UnauthorizedObjectAccessException("Only project owners can archive projects.")
        
        project.status = "archived"
        project.updated_at = self._get_utc_now(timezone_str)
        return project

    def delete_project(self, project_id: str, organization_name: str, actor_id: str) -> None:
        """Permanently delete a project and clean up dependent work items, comments, attachments, and activity records."""
        project = self.get_project(project_id, organization_name)
        if actor_id not in project.members or not project.members[actor_id].is_owner:
            raise UnauthorizedObjectAccessException("Only project owners can delete projects.")
        
        # Clean up dependent work items, comments, attachments, and activity records
        project.work_items.clear()
        project.comments.clear()
        project.attachments.clear()
        project.activity_records.clear()
        project.members.clear()
        
        del self._projects[project_id]

    def create_work_item(
        self,
        project_id: str,
        organization_name: str,
        actor_id: str,
        work_item_id: str,
        title: str,
        status: str = "not_yet_completed",
        priority: str = "medium",
        assignee_id: Optional[str] = None,
        due_date: Optional[date] = None,
        description: str = "",
        position: int = 0,
        timezone_str: str = "UTC",
    ) -> WorkItem:
        """Create a work item within a project."""
        if not work_item_id:
            raise MalformedWorkItemException("Work item ID cannot be empty.")
        
        project = self.get_project(project_id, organization_name)
        if actor_id not in project.members:
            raise UnauthorizedObjectAccessException("User is not a member of this project.")

        valid_statuses = {"not_yet_completed", "in_progress", "completed"}
        if status not in valid_statuses:
            raise InvalidStateTransitionException(f"Invalid work item status: '{status}'.")

        valid_priorities = {"low", "medium", "high", "urgent"}
        if priority not in valid_priorities:
            raise ValidationError(f"Invalid priority: '{priority}'.")

        if assignee_id is not None and assignee_id not in project.members:
            raise ValidationError("Assignee must be a project member.")

        sanitized_desc = self._sanitize_description(description)
        now_dt = self._get_utc_now(timezone_str)

        work_item = WorkItem(
            id=work_item_id,
            title=title,
            status=status,
            priority=priority,
            assignee_id=assignee_id,
            due_date=due_date,
            description=sanitized_desc,
            position=position,
            version=1,
            created_at=now_dt,
            updated_at=now_dt,
        )
        
        work_item.history.append({
            "timestamp": now_dt.isoformat(),
            "actor_id": actor_id,
            "action": "created",
            "changes": {"title": title, "status": status}
        })

        project.work_items[work_item_id] = work_item
        project.updated_at = now_dt
        return work_item

    def update_work_item(
        self,
        project_id: str,
        organization_name: str,
        actor_id: str,
        work_item_id: str,
        title: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assignee_id: Optional[str] = None,
        due_date: Optional[Any] = None,
        clear_due_date: bool = False,
        description: Optional[str] = None,
        position: Optional[int] = None,
        expected_version: Optional[int] = None,
        timezone_str: str = "UTC",
    ) -> WorkItem:
        """Update a work item's fields and record historical changes with optimistic concurrency locking."""
        project = self.get_project(project_id, organization_name)
        if actor_id not in project.members:
            raise UnauthorizedObjectAccessException("User is not a member of this project.")

        if not work_item_id or work_item_id not in project.work_items:
            raise MalformedWorkItemException(f"Work item '{work_item_id}' not found in project.")

        work_item = project.work_items[work_item_id]

        if expected_version is not None and work_item.version != expected_version:
            raise ConcurrentModificationException(
                f"Work item '{work_item_id}' has been modified concurrently. Expected version {expected_version}, but found {work_item.version}."
            )

        changes: dict[str, Any] = {}

        if title is not None:
            if not isinstance(title, str) or not title.strip():
                raise ValidationError("Work item title cannot be empty.")
            changes["title"] = {"old": work_item.title, "new": title}
            work_item.title = title

        if status is not None:
            valid_statuses = {"not_yet_completed", "in_progress", "completed"}
            if status not in valid_statuses:
                raise InvalidStateTransitionException(f"Invalid status value: '{status}'.")
            changes["status"] = {"old": work_item.status, "new": status}
            work_item.status = status

        if priority is not None:
            valid_priorities = {"low", "medium", "high", "urgent"}
            if priority not in valid_priorities:
                raise ValidationError(f"Invalid priority: '{priority}'.")
            changes["priority"] = {"old": work_item.priority, "new": priority}
            work_item.priority = priority

        if assignee_id is not None:
            if assignee_id != "" and assignee_id not in project.members:
                raise ValidationError("Assignee must be a project member.")
            new_assignee = None if assignee_id == "" else assignee_id
            changes["assignee_id"] = {"old": work_item.assignee_id, "new": new_assignee}
            work_item.assignee_id = new_assignee

        if clear_due_date:
            changes["due_date"] = {"old": work_item.due_date, "new": None}
            work_item.due_date = None
        elif due_date is not None:
            changes["due_date"] = {"old": work_item.due_date, "new": due_date}
            work_item.due_date = due_date

        if description is not None:
            sanitized_desc = self._sanitize_description(description)
            changes["description"] = {"old": work_item.description, "new": sanitized_desc}
            work_item.description = sanitized_desc

        if position is not None:
            changes["position"] = {"old": work_item.position, "new": position}
            work_item.position = position

        if changes:
            now_dt = self._get_utc_now(timezone_str)
            work_item.version += 1
            work_item.updated_at = now_dt
            work_item.history.append({
                "timestamp": now_dt.isoformat(),
                "actor_id": actor_id,
                "action": "updated",
                "changes": changes,
                "version": work_item.version
            })
            project.updated_at = now_dt

        return work_item