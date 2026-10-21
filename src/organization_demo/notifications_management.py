"""notifications_management module.

Implements in-app notification handling and asynchronous email delivery
according to the business rules specified for the project.
"""

from __future__ import annotations

import threading
import uuid
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Callable, Dict, List, Optional, Set, Tuple

# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------


class NotificationDeliveryException(Exception):
    """Raised when a notification cannot be delivered to the user."""


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
# Email handling (asynchronous)
# ----------------------------------------------------------------------


@dataclass
class EmailTemplate:
    """Simple container for an email template."""

    subject: str
    body: str  # body may contain placeholders like {token}


def _default_email_sender(to_address: str, subject: str, body: str) -> None:
    """
    Placeholder for real email sending logic.
    In production this would interface with an SMTP server or email service.
    """
    logging.info("Sending email to %s | Subject: %s", to_address, subject)


# ----------------------------------------------------------------------
# Notification service
# ----------------------------------------------------------------------


class NotificationService:
    """Manages notifications and optional email delivery for users."""

    def __init__(
        self,
        email_sender: Callable[[str, str, str], None] = _default_email_sender,
    ) -> None:
        # In-memory stores; replace with persistent storage in a real app.
        self._notifications: Dict[str, List[Notification]] = {}
        self._email_enabled: Dict[str, bool] = {}
        self._email_sender = email_sender
        # Track recently created notifications to avoid duplicates on retries.
        self._generated_keys: Set[Tuple[str, NotificationEventType, Optional[str]]] = set()
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
        with self._lock:
            # Check user notification preferences for comment on followed items or other events
            if event_type == NotificationEventType.COMMENT_ON_FOLLOWED_ITEM:
                # If notifications/email are disabled according to settings, or if we want to respect settings
                # For COMMENT_ON_FOLLOWED_ITEM specifically, requirement states notifications are generated based on user notification settings.
                # If user explicitly turned off preferences (e.g. email enabled is False or a dedicated preference lookup), verify:
                # We can check a general preference check or specific notification preference mapping if present.
                pass

            # More broadly, verify user notification preference for comments on followed items if disabled
            # If the user has explicitly disabled notifications or email/in-app preferences, respect them.
            # Here we check if user has disabled notifications via preference lookup.
            if event_type == NotificationEventType.COMMENT_ON_FOLLOWED_ITEM:
                # Consult user notification settings; if preference is explicitly set to false, skip notification creation.
                # We use is_email_enabled or check an internal preference store if applicable.
                if not self.is_email_enabled(user_id):
                    # If user has disabled preference settings, do not generate comment on followed item notification.
                    return None

            key = self._deduplication_key(user_id, event_type, related_id)

            if key in self._generated_keys:
                # Duplicate detected - return the existing notification if any.
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
            # Email delivery must not affect the primary action.
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

        # Sort: unread first, then by created_at ascending.
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
        raise NotificationDeliveryException(
            f"Notification {notification_id} not found for user {user_id}."
        )

    # ------------------------------------------------------------------
    # Email dispatch
    # ------------------------------------------------------------------

    def _dispatch_email_async(
        self,
        to_address: str,
        template: EmailTemplate,
        notification: Notification,
    ) -> None:
        """
        Send an email in a background thread. Failures are logged and do not
        affect the primary operation.
        """

        def worker() -> None:
            try:
                # Ensure email address is not logged in plain text beyond this scope.
                self._email_sender(
                    to_address,
                    template.subject,
                    template.body.format(token=str(notification.id)),
                )
            except Exception as exc:
                # Wrap any exception in EmailDeliveryException for consistency.
                self._logger.error(
                    "Failed to deliver email for notification %s: %s",
                    notification.id,
                    exc,
                )
                raise EmailDeliveryException(str(exc)) from exc

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

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
        Attempt to send an invitation email.

        Returns True if the email was handed off to the async sender,
        even if delivery later fails. Distinguishes between creation
        success and delivery attempt.
        """
        # Create a notification for the invitation event.
        self.add_notification(
            user_id=user_id,
            event_type=NotificationEventType.INVITATION,
            message="You have been invited to join the organization.",
            related_id=invitation_token,
            send_email=False,
        )

        # Dispatch email asynchronously.
        try:
            self._dispatch_email_async(
                to_address=email_address,
                template=template,
                notification=Notification(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    event_type=NotificationEventType.INVITATION,
                    message="Invitation",
                    related_id=invitation_token,
                ),
            )
            return True
        except EmailDeliveryException:
            # Delivery failure does not roll back invitation creation.
            return False

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