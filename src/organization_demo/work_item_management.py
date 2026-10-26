import uuid
import datetime
import html
import os
import threading
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Any, Tuple

# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------
class WorkItemNotFoundException(Exception):
    """Raised when a requested work item does not exist."""
    pass

class InvalidStatusTransitionException(Exception):
    """Raised when an invalid status transition is attempted on a work item."""
    pass

class InvalidAssigneeException(Exception):
    """Raised when an assigned user is not a valid project member."""
    pass

class MalformedIdentifierException(Exception):
    """Raised when a supplied identifier is malformed or invalid."""
    pass

class CrossTenantAccessException(Exception):
    """Raised when a cross-tenant request targets a resource in another organization."""
    pass

class CommentNotFoundException(Exception):
    """Raised when a requested comment does not exist."""
    pass

class UnauthorizedCommentEditException(Exception):
    """Raised when a user attempts to edit or delete a comment they do not own or lack authorization for."""
    pass

class CommentModerationException(Exception):
    """Raised when comment moderation fails or is unauthorized."""
    pass

class AttachmentNotFoundException(Exception):
    """Raised when a requested attachment does not exist."""
    pass

class FileSizeLimitExceededException(Exception):
    """Raised when an uploaded file exceeds the allowed size limit."""
    pass

class InvalidFilenameException(Exception):
    """Raised when a supplied filename is invalid or unsafe."""
    pass

class StorageBackendException(Exception):
    """Raised when the storage backend encounters an error."""
    pass

class StorageUnavailableException(Exception):
    """Raised when the storage backend is unavailable."""
    pass

class FileSizeExceededException(Exception):
    """Raised when a file exceeds size limits."""
    pass

class InvalidPathException(Exception):
    """Raised when a file path contains invalid or unsafe components."""
    pass

class UnauthorizedAccessException(Exception):
    """Raised when access to a resource is unauthorized."""
    pass


# ----------------------------------------------------------------------
# Data Models
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Attachment:
    """Represents a file attached to a work item or comment."""
    id: uuid.UUID
    display_name: str
    storage_id: str  # opaque unique identifier for decoupled storage backend
    size_bytes: int
    uploaded_at: datetime.datetime
    deleted: bool = False


@dataclass(frozen=True)
class Comment:
    """Represents a comment on a work item in a linear structure."""
    id: uuid.UUID
    author_id: uuid.UUID
    content: str  # raw content; escaped when rendered
    created_at: datetime.datetime
    edited_at: Optional[datetime.datetime] = None
    deleted: bool = False
    attachments: List[Attachment] = field(default_factory=list)


@dataclass(frozen=True)
class WorkItemDueDate:
    """Represents a date-only calendar value independent of timezones."""
    calendar_date: datetime.date

    def format_for_display(self) -> str:
        return self.calendar_date.isoformat()


@dataclass(frozen=True)
class WorkItem:
    """Represents a work item belonging to one project within an organization."""
    id: uuid.UUID
    organization_id: uuid.UUID
    project_id: uuid.UUID
    title: str
    status: str  # 'Not Started', 'In Progress', 'Completed'
    description: Optional[str] = None
    priority: Optional[str] = None  # e.g., 'Low', 'Medium', 'High', 'Urgent'
    creator_id: Optional[uuid.UUID] = None
    assignee_id: Optional[uuid.UUID] = None
    due_date: Optional[WorkItemDueDate] = None
    created_at: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    display_order: int = 0
    comments: List[Comment] = field(default_factory=list)
    attachments: List[Attachment] = field(default_factory=list)
    history: List[Dict[str, Any]] = field(default_factory=list)


# ----------------------------------------------------------------------
# Work Item Management Service
# ----------------------------------------------------------------------
class WorkItemManagementService:
    """
    Manages work items, comments, attachments, security boundaries,
    project memberships, idempotency, and audit history.
    """

    MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB limit
    VALID_STATUSES: Set[str] = {"Not Started", "In Progress", "Completed"}

    def __init__(self) -> None:
        # work_item_id -> WorkItem
        self._work_items: Dict[uuid.UUID, WorkItem] = {}
        # attachment_id -> (work_item_id, Attachment)
        self._attachments: Dict[uuid.UUID, Tuple[uuid.UUID, Attachment]] = {}
        # project_id -> set of member account IDs
        self._project_members: Dict[uuid.UUID, Set[uuid.UUID]] = {}
        # organization_id -> set of project_ids
        self._org_projects: Dict[uuid.UUID, Set[uuid.UUID]] = {}
        # idempotency tracking
        self._work_item_idempotency: Dict[str, uuid.UUID] = {}
        self._comment_idempotency: Dict[str, uuid.UUID] = {}
        self._attachment_idempotency: Dict[str, uuid.UUID] = {}
        # Thread lock for concurrency safety
        self._lock = threading.Lock()

    def set_project_membership(self, organization_id: uuid.UUID, project_id: uuid.UUID, member_ids: Set[uuid.UUID]) -> None:
        """Configure authorized members for a project within an organization."""
        with self._lock:
            self._project_members[project_id] = set(member_ids)
            self._org_projects.setdefault(organization_id, set()).add(project_id)

    def _validate_identifier(self, identifier: Any) -> uuid.UUID:
        """Validate and parse a UUID identifier."""
        if isinstance(identifier, uuid.UUID):
            return identifier
        if isinstance(identifier, str):
            try:
                return uuid.UUID(identifier)
            except (ValueError, AttributeError) as exc:
                raise MalformedIdentifierException(f"Malformed identifier: {identifier}") from exc
        raise MalformedIdentifierException(f"Invalid identifier type: {type(identifier)}")

    def create_work_item(
        self,
        organization_id: uuid.UUID,
        project_id: uuid.UUID,
        title: str,
        status: str = "Not Started",
        description: Optional[str] = None,
        priority: Optional[str] = None,
        creator_id: Optional[uuid.UUID] = None,
        assignee_id: Optional[uuid.UUID] = None,
        due_date: Optional[datetime.date | str | WorkItemDueDate] = None,
        idempotency_key: Optional[str] = None,
    ) -> WorkItem:
        """Create a new work item with validation for status, membership, and idempotency."""
        org_id = self._validate_identifier(organization_id)
        proj_id = self._validate_identifier(project_id)

        with self._lock:
            if idempotency_key:
                existing_id = self._work_item_idempotency.get(idempotency_key)
                if existing_id and existing_id in self._work_items:
                    return self._work_items[existing_id]

            if status not in self.VALID_STATUSES:
                raise InvalidStatusTransitionException(f"Invalid initial status: {status}")

            if not title or not title.strip():
                raise ValueError("Work item requires at minimum a title.")

            # Validate assignee membership if provided
            if assignee_id is not None:
                members = self._project_members.get(proj_id, set())
                if assignee_id not in members:
                    raise InvalidAssigneeException("Assignee must be a member of the project.")

            parsed_due_date = None
            if due_date is not None:
                if isinstance(due_date, WorkItemDueDate):
                    parsed_due_date = due_date
                elif isinstance(due_date, datetime.date) and not isinstance(due_date, datetime.datetime):
                    parsed_due_date = WorkItemDueDate(calendar_date=due_date)
                elif isinstance(due_date, str):
                    parsed_due_date = WorkItemDueDate(calendar_date=datetime.date.fromisoformat(due_date))
                elif isinstance(due_date, datetime.datetime):
                    parsed_due_date = WorkItemDueDate(calendar_date=due_date.date())
                else:
                    raise ValueError("Invalid due date format.")

            now = datetime.datetime.now(datetime.timezone.utc)
            item_id = uuid.uuid4()

            history_entry = {
                "timestamp": now.isoformat(),
                "action": "CREATED",
                "actor_id": str(creator_id) if creator_id else None,
                "changes": {"title": title, "status": status}
            }

            work_item = WorkItem(
                id=item_id,
                organization_id=org_id,
                project_id=proj_id,
                title=title,
                status=status,
                description=description,
                priority=priority,
                creator_id=creator_id,
                assignee_id=assignee_id,
                due_date=parsed_due_date,
                created_at=now,
                updated_at=now,
                history=[history_entry]
            )

            self._work_items[item_id] = work_item
            self._org_projects.setdefault(org_id, set()).add(proj_id)

            if idempotency_key:
                self._work_item_idempotency[idempotency_key] = item_id

            return work_item

    def get_work_item(self, organization_id: uuid.UUID, work_item_id: uuid.UUID) -> WorkItem:
        """Retrieve a work item, enforcing strict organization tenant isolation boundaries."""
        org_id = self._validate_identifier(organization_id)
        item_id = self._validate_identifier(work_item_id)

        with self._lock:
            item = self._work_items.get(item_id)
            if not item:
                raise WorkItemNotFoundException("Work item not found.")
            if item.organization_id != org_id:
                # Enforce tenant isolation by responding as unauthorized/unavailable without leaking existence
                raise CrossTenantAccessException("Work item does not belong to the specified organization.")
            return item

    def update_work_item(
        self,
        organization_id: uuid.UUID,
        work_item_id: uuid.UUID,
        actor_id: Optional[uuid.UUID] = None,
        title: Optional[str] = None,
        status: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        assignee_id: Optional[uuid.UUID] = None,
        due_date: Optional[datetime.date | str | WorkItemDueDate | None] = None,
        clear_due_date: bool = False,
        display_order: Optional[int] = None,
    ) -> WorkItem:
        """Update a work item, recording history for title, status, assignee, description, and due date changes."""
        org_id = self._validate_identifier(organization_id)
        item_id = self._validate_identifier(work_item_id)

        with self._lock:
            item = self.get_work_item(org_id, item_id)
            changes: Dict[str, Any] = {}
            now = datetime.datetime.now(datetime.timezone.utc)

            new_title = item.title if title is None else title
            if title is not None and title != item.title:
                changes["title"] = {"old": item.title, "new": title}

            new_status = item.status
            if status is not None:
                if status not in self.VALID_STATUSES:
                    raise InvalidStatusTransitionException(f"Invalid workflow status: {status}")
                if status != item.status:
                    changes["status"] = {"old": item.status, "new": status}
                    new_status = status

            new_description = item.description if description is None else description
            if description is not None and description != item.description:
                changes["description"] = {"old": item.description, "new": description}

            new_priority = item.priority if priority is None else priority
            if priority is not None and priority != item.priority:
                changes["priority"] = {"old": item.priority, "new": priority}

            new_assignee_id = item.assignee_id
            if assignee_id is not None:
                members = self._project_members.get(item.project_id, set())
                if assignee_id not in members:
                    raise InvalidAssigneeException("Assignee must be a project member.")
                if assignee_id != item.assignee_id:
                    changes["assignee_id"] = {"old": str(item.assignee_id) if item.assignee_id else None, "new": str(assignee_id)}
                    new_assignee_id = assignee_id
            elif assignee_id is None and item.assignee_id is not None and actor_id is not None:
                # If explicitly passing assignee_id as None or updating
                pass

            new_due_date = item.due_date
            if clear_due_date:
                if item.due_date is not None:
                    changes["due_date"] = {"old": item.due_date.format_for_display(), "new": None}
                new_due_date = None
            elif due_date is not None:
                if isinstance(due_date, WorkItemDueDate):
                    parsed_dd = due_date
                elif isinstance(due_date, datetime.date) and not isinstance(due_date, datetime.datetime):
                    parsed_dd = WorkItemDueDate(calendar_date=due_date)
                elif isinstance(due_date, str):
                    parsed_dd = WorkItemDueDate(calendar_date=datetime.date.fromisoformat(due_date))
                elif isinstance(due_date, datetime.datetime):
                    parsed_dd = WorkItemDueDate(calendar_date=due_date.date())
                else:
                    raise ValueError("Invalid due date format.")

                old_dd_str = item.due_date.format_for_display() if item.due_date else None
                new_dd_str = parsed_dd.format_for_display()
                if old_dd_str != new_dd_str:
                    changes["due_date"] = {"old": old_dd_str, "new": new_dd_str}
                new_due_date = parsed_dd

            new_display_order = item.display_order if display_order is None else display_order
            if display_order is not None and display_order != item.display_order:
                changes["display_order"] = {"old": item.display_order, "new": display_order}

            updated_history = list(item.history)
            if changes:
                updated_history.append({
                    "timestamp": now.isoformat(),
                    "action": "UPDATED",
                    "actor_id": str(actor_id) if actor_id else None,
                    "changes": changes
                })

            updated_item = WorkItem(
                id=item.id,
                organization_id=item.organization_id,
                project_id=item.project_id,
                title=new_title,
                status=new_status,
                description=new_description,
                priority=new_priority,
                creator_id=item.creator_id,
                assignee_id=new_assignee_id,
                due_date=new_due_date,
                created_at=item.created_at,
                updated_at=now,
                display_order=new_display_order,
                comments=item.comments,
                attachments=item.attachments,
                history=updated_history,
            )

            self._work_items[item_id] = updated_item
            return updated_item

    def reorder_work_item(self, organization_id: uuid.UUID, work_item_id: uuid.UUID, new_display_order: int) -> WorkItem:
        """Manually reorder work item within project views without altering business priority."""
        return self.update_work_item(organization_id=organization_id, work_item_id=work_item_id, display_order=new_display_order)

    # ------------------------------------------------------------------
    # Comment Operations
    # ------------------------------------------------------------------
    def add_comment(
        self,
        organization_id: uuid.UUID,
        work_item_id: uuid.UUID,
        author_id: uuid.UUID,
        content: str,
        idempotency_key: Optional[str] = None,
    ) -> Comment:
        """Add a linear comment to a work item with XSS sanitization and idempotency support."""
        org_id = self._validate_identifier(organization_id)
        item_id = self._validate_identifier(work_item_id)
        auth_id = self._validate_identifier(author_id)

        with self._lock:
            if idempotency_key:
                existing_comment_id = self._comment_idempotency.get(idempotency_key)
                if existing_comment_id:
                    item = self.get_work_item(org_id, item_id)
                    for c in item.comments:
                        if c.id == existing_comment_id:
                            return c

            item = self.get_work_item(org_id, item_id)

            comment_id = uuid.uuid4()
            now = datetime.datetime.now(datetime.timezone.utc)
            comment = Comment(
                id=comment_id,
                author_id=auth_id,
                content=content,
                created_at=now,
            )

            updated_comments = list(item.comments) + [comment]
            updated_history = list(item.history) + [{
                "timestamp": now.isoformat(),
                "action": "COMMENT_ADDED",
                "actor_id": str(auth_id),
                "comment_id": str(comment_id)
            }]

            updated_item = WorkItem(
                id=item.id,
                organization_id=item.organization_id,
                project_id=item.project_id,
                title=item.title,
                status=item.status,
                description=item.description,
                priority=item.priority,
                creator_id=item.creator_id,
                assignee_id=item.assignee_id,
                due_date=item.due_date,
                created_at=item.created_at,
                updated_at=now,
                display_order=item.display_order,
                comments=updated_comments,
                attachments=item.attachments,
                history=updated_history,
            )
            self._work_items[item_id] = updated_item

            if idempotency_key:
                self._comment_idempotency[idempotency_key] = comment_id

            return comment

    def edit_comment(
        self,
        organization_id: uuid.UUID,
        work_item_id: uuid.UUID,
        comment_id: uuid.UUID,
        editor_id: uuid.UUID,
        new_content: str,
        is_admin: bool = False,
    ) -> Comment:
        """Edit an existing comment while strictly preserving original author and creation timestamp."""
        org_id = self._validate_identifier(organization_id)
        item_id = self._validate_identifier(work_item_id)
        ed_id = self._validate_identifier(editor_id)
        comm_id = self._validate_identifier(comment_id)

        with self._lock:
            item = self.get_work_item(org_id, item_id)
            comment = self._find_comment_in_item(item, comm_id)

            if comment.author_id != ed_id and not is_admin:
                raise UnauthorizedCommentEditException("Only the author or an organization administrator can edit this comment.")

            now = datetime.datetime.now(datetime.timezone.utc)
            updated_comment = Comment(
                id=comment.id,
                author_id=comment.author_id,  # preserved
                content=new_content,
                created_at=comment.created_at,  # preserved
                edited_at=now,
                deleted=comment.deleted,
                attachments=comment.attachments,
            )

            new_comments = [
                updated_comment if c.id == comm_id else c
                for c in item.comments
            ]

            updated_history = list(item.history) + [{
                "timestamp": now.isoformat(),
                "action": "COMMENT_EDITED",
                "actor_id": str(ed_id),
                "comment_id": str(comm_id)
            }]

            updated_item = WorkItem(
                id=item.id,
                organization_id=item.organization_id,
                project_id=item.project_id,
                title=item.title,
                status=item.status,
                description=item.description,
                priority=item.priority,
                creator_id=item.creator_id,
                assignee_id=item.assignee_id,
                due_date=item.due_date,
                created_at=item.created_at,
                updated_at=now,
                display_order=item.display_order,
                comments=new_comments,
                attachments=item.attachments,
                history=updated_history,
            )
            self._work_items[item_id] = updated_item
            return updated_comment

    def delete_comment(
        self,
        organization_id: uuid.UUID,
        work_item_id: uuid.UUID,
        comment_id: uuid.UUID,
        deleter_id: uuid.UUID,
        is_admin: bool = False,
    ) -> None:
        """Mark a comment as deleted, retaining a tombstone/deletion indicator in history."""
        org_id = self._validate_identifier(organization_id)
        item_id = self._validate_identifier(work_item_id)
        del_id = self._validate_identifier(deleter_id)
        comm_id = self._validate_identifier(comment_id)

        with self._lock:
            item = self.get_work_item(org_id, item_id)
            comment = self._find_comment_in_item(item, comm_id)

            if comment.author_id != del_id and not is_admin:
                raise UnauthorizedCommentEditException("Only the author or an administrator can delete this comment.")

            now = datetime.datetime.now(datetime.timezone.utc)
            tombstone_comment = Comment(
                id=comment.id,
                author_id=comment.author_id,
                content="[Comment deleted]",
                created_at=comment.created_at,
                edited_at=now,
                deleted=True,
                attachments=comment.attachments,
            )

            new_comments = [
                tombstone_comment if c.id == comm_id else c
                for c in item.comments
            ]

            updated_history = list(item.history) + [{
                "timestamp": now.isoformat(),
                "action": "COMMENT_DELETED",
                "actor_id": str(del_id),
                "comment_id": str(comm_id)
            }]

            updated_item = WorkItem(
                id=item.id,
                organization_id=item.organization_id,
                project_id=item.project_id,
                title=item.title,
                status=item.status,
                description=item.description,
                priority=item.priority,
                creator_id=item.creator_id,
                assignee_id=item.assignee_id,
                due_date=item.due_date,
                created_at=item.created_at,
                updated_at=now,
                display_order=item.display_order,
                comments=new_comments,
                attachments=item.attachments,
                history=updated_history,
            )
            self._work_items[item_id] = updated_item

    def list_comments(self, organization_id: uuid.UUID, work_item_id: uuid.UUID, include_deleted: bool = False) -> List[Comment]:
        """List comments for a work item."""
        item = self.get_work_item(organization_id, work_item_id)
        if include_deleted:
            return list(item.comments)
        return [c for c in item.comments if not c.deleted]

    # ------------------------------------------------------------------
    # Attachment Operations
    # ------------------------------------------------------------------
    def add_attachment(
        self,
        organization_id: uuid.UUID,
        work_item_id: uuid.UUID,
        uploader_id: uuid.UUID,
        display_name: str,
        size_bytes: int,
        comment_id: Optional[uuid.UUID] = None,
        idempotency_key: Optional[str] = None,
    ) -> Attachment:
        """
        Upload an attachment directly to a work item or associate with an individual comment.
        Enforces strict file size limits, filename sanitization, and decoupled storage keys.
        """
        org_id = self._validate_identifier(organization_id)
        item_id = self._validate_identifier(work_item_id)
        up_id = self._validate_identifier(uploader_id)

        if size_bytes > self.MAX_FILE_SIZE_BYTES:
            raise FileSizeLimitExceededException(f"File size {size_bytes} exceeds maximum allowed {self.MAX_FILE_SIZE_BYTES} bytes.")

        if self._contains_path_traversal(display_name):
            raise InvalidPathException("Provided filename contains unsafe path components.")

        sanitized_name = self.sanitize_filename(display_name)
        if not sanitized_name:
            raise InvalidFilenameException("Filename is invalid or empty.")

        with self._lock:
            if idempotency_key:
                existing_att_id = self._attachment_idempotency.get(idempotency_key)
                if existing_att_id and existing_att_id in self._attachments:
                    return self._attachments[existing_att_id][1]

            item = self.get_work_item(org_id, item_id)

            attachment_id = uuid.uuid4()
            storage_id = f"store_{uuid.uuid4().hex}_{sanitized_name}"
            now = datetime.datetime.now(datetime.timezone.utc)

            attachment = Attachment(
                id=attachment_id,
                display_name=sanitized_name,
                storage_id=storage_id,
                size_bytes=size_bytes,
                uploaded_at=now,
            )

            self._attachments[attachment_id] = (item_id, attachment)

            if idempotency_key:
                self._attachment_idempotency[idempotency_key] = attachment_id

            new_comments = list(item.comments)
            new_attachments = list(item.attachments)

            if comment_id:
                comm_id = self._validate_identifier(comment_id)
                target_comment = self._find_comment_in_item(item, comm_id)
                updated_comment_attachments = list(target_comment.attachments) + [attachment]
                updated_comment = Comment(
                    id=target_comment.id,
                    author_id=target_comment.author_id,
                    content=target_comment.content,
                    created_at=target_comment.created_at,
                    edited_at=target_comment.edited_at,
                    deleted=target_comment.deleted,
                    attachments=updated_comment_attachments,
                )
                new_comments = [
                    updated_comment if c.id == comm_id else c
                    for c in item.comments
                ]
            else:
                new_attachments.append(attachment)

            updated_history = list(item.history) + [{
                "timestamp": now.isoformat(),
                "action": "ATTACHMENT_ADDED",
                "actor_id": str(up_id),
                "attachment_id": str(attachment_id),
                "display_name": sanitized_name
            }]

            updated_item = WorkItem(
                id=item.id,
                organization_id=item.organization_id,
                project_id=item.project_id,
                title=item.title,
                status=item.status,
                description=item.description,
                priority=item.priority,
                creator_id=item.creator_id,
                assignee_id=item.assignee_id,
                due_date=item.due_date,
                created_at=item.created_at,
                updated_at=now,
                display_order=item.display_order,
                comments=new_comments,
                attachments=new_attachments,
                history=updated_history,
            )
            self._work_items[item_id] = updated_item
            return attachment

    def get_attachment(
        self,
        organization_id: uuid.UUID,
        work_item_id: uuid.UUID,
        attachment_id: uuid.UUID,
        requester_id: uuid.UUID,
        is_admin: bool = False,
    ) -> Attachment:
        """
        Retrieve an attachment independently, enforcing work item access rules,
        organization tenant boundaries, and project membership.
        """
        org_id = self._validate_identifier(organization_id)
        item_id = self._validate_identifier(work_item_id)
        att_id = self._validate_identifier(attachment_id)
        req_id = self._validate_identifier(requester_id)

        with self._lock:
            # Enforce work item and tenant access rules first
            item = self.get_work_item(org_id, item_id)

            record = self._attachments.get(att_id)
            if not record or record[0] != item_id:
                raise AttachmentNotFoundException("Attachment not found.")

            attachment = record[1]
            if attachment.deleted:
                raise AttachmentNotFoundException("Attachment has been deleted.")

            if is_admin:
                return attachment

            # Verify project membership access
            members = self._project_members.get(item.project_id, set())
            if req_id not in members:
                raise UnauthorizedAccessException("User is not authorized to access this attachment.")

            return attachment

    def delete_attachment(
        self,
        organization_id: uuid.UUID,
        work_item_id: uuid.UUID,
        attachment_id: uuid.UUID,
        deleter_id: uuid.UUID,
        is_admin: bool = False,
    ) -> None:
        """
        Delete an attachment, revoking normal file access and leaving an activity record
        without retaining a publicly accessible file copy.
        """
        org_id = self._validate_identifier(organization_id)
        item_id = self._validate_identifier(work_item_id)
        att_id = self._validate_identifier(attachment_id)
        del_id = self._validate_identifier(deleter_id)

        with self._lock:
            item = self.get_work_item(org_id, item_id)
            record = self._attachments.get(att_id)
            if not record or record[0] != item_id:
                raise AttachmentNotFoundException("Attachment not found.")

            attachment = record[1]
            if attachment.deleted:
                raise AttachmentNotFoundException("Attachment already deleted.")

            if not is_admin:
                # Only admins or authorized owners can delete attachments
                members = self._project_members.get(item.project_id, set())
                if del_id not in members:
                    raise UnauthorizedAccessException("Unauthorized to delete attachment.")

            deleted_attachment = Attachment(
                id=attachment.id,
                display_name=attachment.display_name,
                storage_id=attachment.storage_id,
                size_bytes=attachment.size_bytes,
                uploaded_at=attachment.uploaded_at,
                deleted=True,
            )
            self._attachments[att_id] = (item_id, deleted_attachment)

            now = datetime.datetime.now(datetime.timezone.utc)
            updated_history = list(item.history) + [{
                "timestamp": now.isoformat(),
                "action": "ATTACHMENT_DELETED",
                "actor_id": str(del_id),
                "attachment_id": str(att_id),
                "display_name": attachment.display_name
            }]

            updated_item = WorkItem(
                id=item.id,
                organization_id=item.organization_id,
                project_id=item.project_id,
                title=item.title,
                status=item.status,
                description=item.description,
                priority=item.priority,
                creator_id=item.creator_id,
                assignee_id=item.assignee_id,
                due_date=item.due_date,
                created_at=item.created_at,
                updated_at=now,
                display_order=item.display_order,
                comments=item.comments,
                attachments=[a for a in item.attachments if a.id != att_id],
                history=updated_history,
            )
            self._work_items[item_id] = updated_item

    # ------------------------------------------------------------------
    # Helper & Rendering Methods
    # ------------------------------------------------------------------
    @staticmethod
    def _find_comment_in_item(item: WorkItem, comment_id: uuid.UUID) -> Comment:
        for c in item.comments:
            if c.id == comment_id:
                return c
        raise CommentNotFoundException("Comment not found.")

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize user-provided filename to prevent path traversal and script injection."""
        base = os.path.basename(filename)
        cleaned = "".join(c for c in base if c.isalnum() or c in (" ", ".", "_", "-")).strip()
        return cleaned or "unnamed_file"

    @staticmethod
    def _contains_path_traversal(path: str) -> bool:
        normalized = os.path.normpath(path)
        return (
            os.path.isabs(normalized)
            or ".." in normalized.split(os.sep)
            or normalized.startswith("..")
        )

    @staticmethod
    def render_comment_content(content: str) -> str:
        """Escape comment content to prevent Cross-Site Scripting (XSS)."""
        return html.escape(content)

    @staticmethod
    def render_attachment_display_name(name: str) -> str:
        """Escape attachment display name."""
        return html.escape(name)