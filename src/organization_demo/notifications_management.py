from __future__ import annotations

import threading
import uuid
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Callable, Dict, List, Optional, Set, Tuple, Any

# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------


class NotificationDeliveryException(Exception):
    """Raised when a notification cannot be delivered to the user."""


class NotificationNotFoundException(Exception):
    """Raised when a requested notification cannot be found."""


class EmailSendException(Exception):
    """Raised when sending an email fails."""


class TemplateNotFoundException(Exception):
    """Raised when a requested email template cannot be found."""


class InvalidNotificationPreferenceException(Exception):
    """Raised when an invalid notification preference is supplied."""


class EmailDeliveryException(Exception):
    """Raised when sending an email fails."""


class InvalidEmailTokenException(Exception):
    """Raised when an email token is malformed or expired."""


# ----------------------------------------------------------------------
# Core data structures
# ----------------------------------------------------------------------


class NotificationEventType(Enum):
    """Types of events that can generate a notification."""

    WORK_ITEM_ASSIGNED = auto()
    COMMENT_MENTION = auto()
    COMMENT_ON_FOLLOWED_ITEM = auto()
    INVITATION = auto()
    OTHER = auto()


@dataclass(frozen=True)
class Notification:
    """Immutable representation of a user notification."""

    id: uuid.UUID
    user_id: str
    event_type: NotificationEventType
    message: str
    related_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    read_at: Optional[datetime] = None

    def is_unread(self) -> bool:
        """Return True if the notification has not been marked as read."""
        return self.read_at is None


# ----------------------------------------------------------------------
# Email handling (asynchronous with retry & monitoring)
# ----------------------------------------------------------------------


@dataclass
class EmailTemplate:
    """Simple container for an email template."""

    subject: str
    body: str  # body may contain placeholders like {token}


@dataclass
class EmailJobStatus:
    """Operational visibility record for an email background dispatch job."""

    job_id: str
    to_address_masked: str
    notification_id: Optional[str]
    attempts: int
    max_attempts: int
    status: str  # e.g., "PENDING", "SUCCESS", "FAILED"
    last_error: Optional[str] = None
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def _default_email_sender(to_address: str, subject: str, body: str) -> None:
    """
    Placeholder for real email sending logic.
    In production this would interface with an SMTP server or email service.
    """
    logging.info("Sending email to recipient | Subject: %s", subject)


# ----------------------------------------------------------------------
# Notification service
# ----------------------------------------------------------------------


class NotificationService:
    """Manages notifications and optional email delivery for users with robust retry and monitoring."""

    def __init__(
        self,
        email_sender: Callable[[str, str, str], None] = _default_email_sender,
        max_email_retries: int = 3,
        backoff_base_seconds: float = 0.5,
    ) -> None:
        # In-memory stores; replace with persistent storage in a real app.
        self._notifications: Dict[str, List[Notification]] = {}
        self._email_enabled: Dict[str, bool] = {}
        self._email_sender = email_sender
        self._max_email_retries = max_email_retries
        self._backoff_base_seconds = backoff_base_seconds
        
        # Operational metrics and job status tracking for visibility
        self._email_job_statuses: Dict[str, EmailJobStatus] = {}
        self._total_emails_dispatched: int = 0
        self._total_emails_failed: int = 0
        self._total_emails_retried: int = 0

        # Track recently created notifications to avoid duplicates on retries.
        self._generated_keys: Set[Tuple[str, NotificationEventType, Optional[str]]] = set()
        # Track dispatched email notification IDs to ensure idempotent/deduplicated sending on retries.
        self._dispatched_email_notification_ids: Set[str] = set()
        self._lock = threading.Lock()
        self._logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------
    # Preference handling
    # ------------------------------------------------------------------

    def set_email_notifications_enabled(self, user_id: str, enabled: bool) -> None:
        """Enable or disable email notifications for a user."""
        if not isinstance(enabled, bool):
            raise InvalidNotificationPreferenceException(
                "Enabled flag must be a boolean."
            )
        with self._lock:
            self._email_enabled[user_id] = enabled

    def is_email_enabled(self, user_id: str) -> bool:
        """Return True if the user has email notifications enabled."""
        with self._lock:
            return self._email_enabled.get(user_id, True)  # default to enabled

    # ------------------------------------------------------------------
    # Notification creation
    # ------------------------------------------------------------------

    def _deduplication_key(
        self,
        user_id: str,
        event_type: NotificationEventType,
        related_id: Optional[str],
    ) -> Tuple[str, NotificationEventType, Optional[str]]:
        return (user_id, event_type, related_id)

    def add_notification(
        self,
        user_id: str,
        event_type: NotificationEventType,
        message: str,
        related_id: Optional[str] = None,
        send_email: bool = False,
        email_template: Optional[EmailTemplate] = None,
        email_address: Optional[str] = None,
    ) -> Optional[Notification]:
        """
        Create a notification for a user.

        Comments on followed items and other event types verify user notification settings.
        Duplicate notifications (same user, event type and related_id) are
        ignored to satisfy the "no duplicate on retry" rule.
        """
        should_dispatch_email = False

        with self._lock:
            if event_type == NotificationEventType.COMMENT_ON_FOLLOWED_ITEM:
                if not self.is_email_enabled(user_id):
                    return None

            key = self._deduplication_key(user_id, event_type, related_id)

            if key in self._generated_keys:
                existing = next(
                    (
                        n
                        for n in self._notifications.get(user_id, [])
                        if n.event_type == event_type and n.related_id == related_id
                    ),
                    None,
                )
                if existing:
                    return existing

            notification = Notification(
                id=uuid.uuid4(),
                user_id=user_id,
                event_type=event_type,
                message=message,
                related_id=related_id,
            )
            self._notifications.setdefault(user_id, []).append(notification)
            self._generated_keys.add(key)

            if send_email and email_template and email_address and self.is_email_enabled(user_id):
                note_id_str = str(notification.id)
                if note_id_str not in self._dispatched_email_notification_ids:
                    self._dispatched_email_notification_ids.add(note_id_str)
                    should_dispatch_email = True

        if should_dispatch_email and email_template and email_address:
            self._dispatch_email_async(email_address, email_template, notification)

        return notification

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def list_notifications(self, user_id: str) -> List[Notification]:
        """
        Return a snapshot of the user's notifications ordered by creation time,
        with unread items first.
        """
        with self._lock:
            notifications = list(self._notifications.get(user_id, []))

        notifications.sort(
            key=lambda n: (n.read_at is not None, n.created_at)
        )
        return notifications

    # ------------------------------------------------------------------
    # Mark as read
    # ------------------------------------------------------------------

    def mark_as_read(self, user_id: str, notification_id: uuid.UUID) -> None:
        """
        Mark a specific notification as read. Does not delete the notification.
        """
        with self._lock:
            user_notes = self._notifications.get(user_id, [])
            for idx, note in enumerate(user_notes):
                if note.id == notification_id:
                    if note.read_at is None:
                        updated = Notification(
                            id=note.id,
                            user_id=note.user_id,
                            event_type=note.event_type,
                            message=note.message,
                            related_id=note.related_id,
                            created_at=note.created_at,
                            read_at=datetime.now(timezone.utc),
                        )
                        user_notes[idx] = updated
                    return
        raise NotificationNotFoundException(
            f"Notification {notification_id} not found for user {user_id}."
        )

    # ------------------------------------------------------------------
    # Email dispatch & monitoring visibility
    # ------------------------------------------------------------------

    def _mask_email(self, email: str) -> str:
        """Avoid logging raw personal PII by masking email addresses."""
        if not email or "@" not in email:
            return "***"
        parts = email.split("@")
        name = parts[0]
        domain = parts[1]
        masked_name = name[:2] + "***" if len(name) > 2 else "***"
        return f"{masked_name}@{domain}"

    def _dispatch_email_async(
        self,
        to_address: str,
        template: EmailTemplate,
        notification: Notification,
    ) -> str:
        """
        Send an email in a background thread with retry limits, exponential backoff,
        and full operational metric tracking.
        Returns the background job ID.
        """
        job_id = str(uuid.uuid4())
        masked_address = self._mask_email(to_address)

        job_status = EmailJobStatus(
            job_id=job_id,
            to_address_masked=masked_address,
            notification_id=str(notification.id),
            attempts=0,
            max_attempts=self._max_email_retries,
            status="PENDING",
        )

        with self._lock:
            self._email_job_statuses[job_id] = job_status

        def worker() -> None:
            attempts = 0
            success = False
            last_exc: Optional[Exception] = None

            while attempts < self._max_email_retries and not success:
                attempts += 1
                with self._lock:
                    job_status.attempts = attempts
                    job_status.updated_at = datetime.now(timezone.utc)

                try:
                    self._email_sender(
                        to_address,
                        template.subject,
                        template.body.format(token=str(notification.id)),
                    )
                    success = True
                    with self._lock:
                        job_status.status = "SUCCESS"
                        job_status.updated_at = datetime.now(timezone.utc)
                        self._total_emails_dispatched += 1
                    self._logger.info(
                        "Successfully delivered email (Job ID: %s, Recipient: %s, Attempt: %d)",
                        job_id,
                        masked_address,
                        attempts,
                    )
                except Exception as exc:
                    last_exc = exc
                    with self._lock:
                        job_status.last_error = str(exc)
                        job_status.updated_at = datetime.now(timezone.utc)
                        self._total_emails_retried += 1

                    self._logger.warning(
                        "Email dispatch attempt %d/%d failed for Job ID %s (Recipient: %s): %s",
                        attempts,
                        self._max_email_retries,
                        job_id,
                        masked_address,
                        exc,
                    )
                    if attempts < self._max_email_retries:
                        backoff = self._backoff_base_seconds * (2 ** (attempts - 1))
                        time.sleep(backoff)

            if not success:
                with self._lock:
                    job_status.status = "FAILED"
                    job_status.updated_at = datetime.now(timezone.utc)
                    self._total_emails_failed += 1

                self._logger.error(
                    "Failed background email job %s after %d attempts for notification %s. Recipient: %s. Error: %s",
                    job_id,
                    attempts,
                    notification.id,
                    masked_address,
                    last_exc,
                )

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return job_id

    def get_email_job_status(self, job_id: str) -> Optional[EmailJobStatus]:
        """Expose operational monitoring visibility for an email dispatch job."""
        with self._lock:
            status = self._email_job_statuses.get(job_id)
            if status is None:
                return None
            return EmailJobStatus(
                job_id=status.job_id,
                to_address_masked=status.to_address_masked,
                notification_id=status.notification_id,
                attempts=status.attempts,
                max_attempts=status.max_attempts,
                status=status.status,
                last_error=status.last_error,
                updated_at=status.updated_at,
            )

    def get_email_metrics(self) -> Dict[str, int]:
        """Return operational metrics counters for background email dispatch."""
        with self._lock:
            return {
                "dispatched": self._total_emails_dispatched,
                "failed": self._total_emails_failed,
                "retried": self._total_emails_retried,
                "active_jobs": len(self._email_job_statuses),
            }

    # ------------------------------------------------------------------
    # Invitation handling (special case)
    # ------------------------------------------------------------------

    def send_invitation(
        self,
        user_id: str,
        email_address: str,
        invitation_token: str,
        template: EmailTemplate,
    ) -> bool:
        """
        Attempt to send an invitation email with deduplication to prevent duplicate sends on retries.

        Returns True if the email was handed off to the async sender,
        even if delivery later fails. Distinguishes between creation
        success and delivery attempt.
        """
        self.add_notification(
            user_id=user_id,
            event_type=NotificationEventType.INVITATION,
            message="You have been invited to join the organization.",
            related_id=invitation_token,
            send_email=False,
        )

        notif_id = uuid.uuid4()
        notif_id_str = str(notif_id)
        dispatch_needed = False

        with self._lock:
            if invitation_token not in self._dispatched_email_notification_ids:
                self._dispatched_email_notification_ids.add(invitation_token)
                dispatch_needed = True

        if not dispatch_needed:
            return True

        try:
            self._dispatch_email_async(
                to_address=email_address,
                template=template,
                notification=Notification(
                    id=notif_id,
                    user_id=user_id,
                    event_type=NotificationEventType.INVITATION,
                    message="Invitation",
                    related_id=invitation_token,
                ),
            )
            return True
        except Exception as exc:
            raise EmailSendException(f"Failed to initiate email send for invitation: {exc}") from exc

    # ------------------------------------------------------------------
    # Token validation (example utility)
    # ------------------------------------------------------------------

    def validate_email_token(self, token: str) -> None:
        """
        Validate a token used in email links (e.g., password reset).

        Raises InvalidEmailTokenException if the token is malformed.
        """
        if not token or len(token) < 10:
            raise InvalidEmailTokenException("Token is invalid or too short.")


# ----------------------------------------------------------------------
# Module-level singleton for convenience
# ----------------------------------------------------------------------


notification_service = NotificationService()