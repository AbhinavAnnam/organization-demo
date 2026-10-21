import uuid
import datetime
import html
import os
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------
class ModerationPermissionException(Exception):
    """Raised when a user without moderation rights attempts to moderate a comment."""
    pass

class CommentNotFoundException(Exception):
    """Raised when a requested comment does not exist."""
    pass

class FileTooLargeException(Exception):
    """Raised when an uploaded file exceeds the allowed size limit."""
    pass

class PathTraversalException(Exception):
    """Raised when a file path contains traversal components."""
    pass

class UploadFailedException(Exception):
    """Raised when an upload operation fails for an unexpected reason."""
    pass

class InvalidFilePathException(Exception):
    """Raised when a supplied file path is invalid or unsafe."""
    pass

class UnauthorizedAttachmentAccessException(Exception):
    """Raised when a user attempts to access an attachment without proper authorization."""
    pass

class AttachmentNotFoundException(Exception):
    """Raised when a requested attachment does not exist."""
    pass

# ----------------------------------------------------------------------
# Data Models
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class Attachment:
    """Represents a file attached to a comment or work item."""
    id: uuid.UUID
    display_name: str
    storage_id: str  # opaque identifier for storage backend
    size_bytes: int
    uploaded_at: datetime.datetime
    deleted: bool = False

@dataclass(frozen=True)
class Comment:
    """Represents a comment on a work item."""
    id: uuid.UUID
    author_id: uuid.UUID
    content: str  # raw content; will be escaped when rendered
    created_at: datetime.datetime
    edited_at: Optional[datetime.datetime] = None
    deleted: bool = False
    attachments: List[Attachment] = field(default_factory=list)

# ----------------------------------------------------------------------
# Service
# ----------------------------------------------------------------------
class CommentService:
    """
    In-memory comment and attachment management service.
    """

    MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB limit

    def __init__(self) -> None:
        # Maps work_item_id -> list of comments
        self._comments: Dict[uuid.UUID, List[Comment]] = {}
        # Maps attachment_id -> Attachment
        self._attachments: Dict[uuid.UUID, Attachment] = {}

    # ------------------------------------------------------------------
    # Comment Operations
    # ------------------------------------------------------------------
    def add_comment(
        self,
        work_item_id: uuid.UUID,
        author_id: uuid.UUID,
        content: str,
    ) -> Comment:
        """Create and store a new comment on the specified work item."""
        comment = Comment(
            id=uuid.uuid4(),
            author_id=author_id,
            content=content,
            created_at=datetime.datetime.utcnow(),
        )
        self._comments.setdefault(work_item_id, []).append(comment)
        return comment

    def edit_comment(
        self,
        work_item_id: uuid.UUID,
        comment_id: uuid.UUID,
        editor_id: uuid.UUID,
        new_content: str,
        is_admin: bool = False,
    ) -> Comment:
        """Edit an existing comment if the editor is the author or an admin."""
        comment = self._find_comment(work_item_id, comment_id)
        if comment.author_id != editor_id and not is_admin:
            raise ModerationPermissionException(
                "Only the author or an administrator can edit this comment."
            )
        updated = Comment(
            id=comment.id,
            author_id=comment.author_id,
            content=new_content,
            created_at=comment.created_at,
            edited_at=datetime.datetime.utcnow(),
            deleted=comment.deleted,
            attachments=comment.attachments,
        )
        self._replace_comment(work_item_id, updated)
        return updated

    def delete_comment(
        self,
        work_item_id: uuid.UUID,
        comment_id: uuid.UUID,
        deleter_id: uuid.UUID,
        is_admin: bool = False,
    ) -> None:
        """Mark a comment as deleted; content remains in history."""
        comment = self._find_comment(work_item_id, comment_id)
        if comment.author_id != deleter_id and not is_admin:
            raise ModerationPermissionException(
                "Only the author or an administrator can delete this comment."
            )
        deleted_comment = Comment(
            id=comment.id,
            author_id=comment.author_id,
            content=comment.content,
            created_at=comment.created_at,
            edited_at=comment.edited_at,
            deleted=True,
            attachments=comment.attachments,
        )
        self._replace_comment(work_item_id, deleted_comment)

    def list_comments(
        self,
        work_item_id: uuid.UUID,
        include_deleted: bool = False,
    ) -> List[Comment]:
        """Return comments for a work item, optionally including deleted ones."""
        comments = self._comments.get(work_item_id, [])
        if include_deleted:
            return list(comments)
        return [c for c in comments if not c.deleted]

    def get_comment(
        self,
        work_item_id: uuid.UUID,
        comment_id: uuid.UUID,
        include_deleted: bool = False,
    ) -> Comment:
        """Retrieve a specific comment."""
        comment = self._find_comment(work_item_id, comment_id)
        if comment.deleted and not include_deleted:
            raise CommentNotFoundException("Comment has been deleted.")
        return comment

    # ------------------------------------------------------------------
    # Attachment Operations
    # ------------------------------------------------------------------
    def add_attachment(
        self,
        work_item_id: uuid.UUID,
        comment_id: Optional[uuid.UUID],
        uploader_id: uuid.UUID,
        display_name: str,
        storage_id: str,
        size_bytes: int,
    ) -> Attachment:
        """
        Associate an attachment with a work item or a specific comment.
        Raises FileTooLargeException if size exceeds limit.
        """
        if size_bytes > self.MAX_FILE_SIZE_BYTES:
            raise FileTooLargeException(
                f"File size {size_bytes} exceeds maximum allowed {self.MAX_FILE_SIZE_BYTES}."
            )
        if self._contains_path_traversal(display_name):
            raise PathTraversalException("File name contains unsafe path components.")
        attachment = Attachment(
            id=uuid.uuid4(),
            display_name=display_name,
            storage_id=storage_id,
            size_bytes=size_bytes,
            uploaded_at=datetime.datetime.utcnow(),
        )
        self._attachments[attachment.id] = attachment
        # Link to comment or work item
        if comment_id:
            comment = self._find_comment(work_item_id, comment_id)
            updated = Comment(
                id=comment.id,
                author_id=comment.author_id,
                content=comment.content,
                created_at=comment.created_at,
                edited_at=comment.edited_at,
                deleted=comment.deleted,
                attachments=comment.attachments + [attachment],
            )
            self._replace_comment(work_item_id, updated)
        else:
            # Attachments directly to work item are stored in a special comment with id None
            # For simplicity, we store them in a dedicated list per work item
            self._comments.setdefault(work_item_id, []).append(
                Comment(
                    id=uuid.uuid4(),
                    author_id=uploader_id,
                    content="",
                    created_at=datetime.datetime.utcnow(),
                    attachments=[attachment],
                )
            )
        return attachment

    def delete_attachment(
        self,
        attachment_id: uuid.UUID,
        deleter_id: uuid.UUID,
        is_admin: bool = False,
    ) -> None:
        """Mark an attachment as deleted; historical record remains."""
        attachment = self._attachments.get(attachment_id)
        if not attachment:
            raise AttachmentNotFoundException("Attachment does not exist.")
        # For simplicity, we do not track ownership; admins can delete
        if not is_admin:
            raise UnauthorizedAttachmentAccessException(
                "Only administrators can delete attachments."
            )
        deleted = Attachment(
            id=attachment.id,
            display_name=attachment.display_name,
            storage_id=attachment.storage_id,
            size_bytes=attachment.size_bytes,
            uploaded_at=attachment.uploaded_at,
            deleted=True,
        )
        self._attachments[attachment_id] = deleted

    def get_attachment(
        self,
        attachment_id: uuid.UUID,
        requester_id: uuid.UUID,
        is_admin: bool = False,
    ) -> Attachment:
        """Retrieve an attachment if the requester is authorized."""
        attachment = self._attachments.get(attachment_id)
        if not attachment or attachment.deleted:
            raise AttachmentNotFoundException("Attachment not found.")
        # Authorization: in real system, check work item/project membership
        if not is_admin:
            raise UnauthorizedAttachmentAccessException(
                "User is not authorized to access this attachment."
            )
        return attachment

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------
    def _find_comment(
        self,
        work_item_id: uuid.UUID,
        comment_id: uuid.UUID,
    ) -> Comment:
        comments = self._comments.get(work_item_id, [])
        for c in comments:
            if c.id == comment_id:
                return c
        raise CommentNotFoundException("Comment not found.")

    def _replace_comment(
        self,
        work_item_id: uuid.UUID,
        updated_comment: Comment,
    ) -> None:
        comments = self._comments.get(work_item_id, [])
        for idx, c in enumerate(comments):
            if c.id == updated_comment.id:
                comments[idx] = updated_comment
                return
        raise CommentNotFoundException("Comment not found for replacement.")

    @staticmethod
    def _contains_path_traversal(path: str) -> bool:
        """Detects unsafe path components like '..' or absolute paths."""
        normalized = os.path.normpath(path)
        return (
            os.path.isabs(normalized)
            or ".." in normalized.split(os.sep)
            or normalized.startswith("..")
        )

    # ------------------------------------------------------------------
    # Rendering Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def render_comment_content(content: str) -> str:
        """Escape comment content to prevent XSS."""
        return html.escape(content)

    @staticmethod
    def render_attachment_display_name(name: str) -> str:
        """Escape attachment display name."""
        return html.escape(name)