"""Search, dashboard, and activity history management service module."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Any

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None  # type: ignore


class SearchIndexingException(Exception):
    """Raised when search indexing encounters an error."""


class UnauthorizedSearchAccessException(Exception):
    """Raised when a user attempts to search content they lack access to."""


class ActivityLogImmutableException(Exception):
    """Raised when an attempt is made to modify an immutable activity record."""


def compute_relative_time_label(target_dt: datetime, current_dt: datetime | None = None) -> str:
    """Compute relative time labels ('today', 'tomorrow', 'yesterday', or formatted date) dynamically."""
    if current_dt is None:
        current_dt = datetime.now(timezone.utc)
    
    if target_dt.tzinfo is not None and current_dt.tzinfo is not None:
        target_dt_utc = target_dt.astimezone(timezone.utc)
        current_dt_utc = current_dt.astimezone(timezone.utc)
    else:
        target_dt_utc = target_dt
        current_dt_utc = current_dt

    t_date = target_dt_utc.date()
    c_date = current_dt_utc.date()
    delta_days = (t_date - c_date).days

    if delta_days == 0:
        return "today"
    elif delta_days == 1:
        return "tomorrow"
    elif delta_days == -1:
        return "yesterday"
    elif 1 < delta_days <= 7:
        return f"in {delta_days} days"
    elif -7 <= delta_days < -1:
        return f"{abs(delta_days)} days ago"
    else:
        return t_date.isoformat()


@dataclass(frozen=True)
class ActivityEntry:
    """An immutable recorded activity entry."""

    activity_id: str
    organization_id: str
    action: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    actor_id: str | None = None
    actor_name: str | None = None
    target_type: str = ""
    target_id: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def __setattr__(self, key: str, value: Any) -> None:
        """Enforce immutability on activity entries."""
        if hasattr(self, key):
            raise ActivityLogImmutableException("Activity records are append-only and immutable.")
        super().__setattr__(key, value)


@dataclass
class SearchResult:
    """A single search match result with surrounding context."""

    item_type: str
    item_id: str
    title: str
    snippet: str
    organization_id: str
    project_id: str | None = None


@dataclass
class DashboardSummary:
    """Dashboard summary metrics and lists for a user within an organization."""

    organization_id: str
    user_id: str
    active_projects: list[dict[str, Any]] = field(default_factory=list)
    assigned_work_items: list[dict[str, Any]] = field(default_factory=list)
    recently_updated_items: list[dict[str, Any]] = field(default_factory=list)
    empty_state_message: str | None = None


class SearchService:
    """Manages search indexing, access-controlled searching, dashboard metrics, and activity logs."""

    def __init__(self) -> None:
        self._index: list[dict[str, Any]] = []
        self._activities: list[ActivityEntry] = []

    def index_document(
        self,
        organization_id: str,
        project_id: str | None,
        item_type: str,
        item_id: str,
        title: str,
        content: str,
        allowed_user_ids: list[str],
        comments: list[str] | None = None,
    ) -> None:
        """Asynchronously or synchronously index an operational document for search, including comments."""
        try:
            doc = {
                "organization_id": organization_id,
                "project_id": project_id,
                "item_type": item_type,
                "item_id": item_id,
                "title": title,
                "content": content,
                "comments": comments or [],
                "allowed_user_ids": set(allowed_user_ids),
                "is_active": True,
            }
            # Remove existing entry if re-indexing
            self._index = [
                d for d in self._index
                if not (d["item_type"] == item_type and d["item_id"] == item_id)
            ]
            self._index.append(doc)
        except Exception as exc:
            raise SearchIndexingException(f"Failed to index document {item_id}: {exc}") from exc

    def remove_document(self, item_type: str, item_id: str) -> None:
        """Remove or restrict access to a document in the search index."""
        self._index = [
            d for d in self._index
            if not (d["item_type"] == item_type and d["item_id"] == item_id)
        ]

    def search(
        self,
        user_id: str,
        organization_id: str,
        query: str,
        user_project_ids: list[str],
        limit: int = 50,
        offset: int = 0,
    ) -> list[SearchResult]:
        """Search accessible operational content with partial matching, access boundaries, and pagination."""
        if not user_id or not organization_id:
            raise UnauthorizedSearchAccessException("User identity and organization scope are required for searching.")

        results: list[SearchResult] = []
        query_lower = query.lower()
        project_ids_set = set(user_project_ids)

        for doc in self._index:
            if doc["organization_id"] != organization_id:
                continue
            if not doc.get("is_active", True):
                continue
            # Enforce project access if project restricted
            if doc["project_id"] and doc["project_id"] not in project_ids_set:
                continue
            # Enforce user access permission boundary
            if user_id not in doc["allowed_user_ids"]:
                continue

            title = doc["title"]
            content = doc["content"]
            comments = doc.get("comments", [])
            title_lower = title.lower()
            content_lower = content.lower()
            comments_lower = [c.lower() for c in comments]

            matched = False
            snippet_source = content

            if query_lower in title_lower or query_lower in content_lower:
                matched = True
            else:
                for c_text in comments_lower:
                    if query_lower in c_text:
                        matched = True
                        snippet_source = comments[comments_lower.index(c_text)]
                        break

            if matched:
                snippet = snippet_source[:150]
                snippet_lower = snippet_source.lower()
                if query_lower in snippet_lower:
                    idx = snippet_lower.find(query_lower)
                    start = max(0, idx - 40)
                    end = min(len(snippet_source), idx + 110)
                    snippet = snippet_source[start:end]

                results.append(
                    SearchResult(
                        item_type=doc["item_type"],
                        item_id=doc["item_id"],
                        title=title,
                        snippet=snippet,
                        organization_id=doc["organization_id"],
                        project_id=doc["project_id"],
                    )
                )

        # Stable ordering across pages using item_type and item_id as secondary keys
        sorted_results = sorted(results, key=lambda x: (x.item_type, x.item_id))
        return sorted_results[offset:offset + limit]

    def record_activity(
        self,
        organization_id: str,
        action: str,
        actor_id: str | None = None,
        actor_name: str | None = None,
        target_type: str = "",
        target_id: str = "",
        details: dict[str, Any] | None = None,
    ) -> ActivityEntry:
        """Record a significant user or system activity into the append-only activity feed."""
        entry = ActivityEntry(
            activity_id=f"act_{len(self._activities) + 1}_{int(datetime.now(timezone.utc).timestamp())}",
            organization_id=organization_id,
            action=action,
            timestamp=datetime.now(timezone.utc),
            actor_id=actor_id,
            actor_name=actor_name,
            target_type=target_type,
            target_id=target_id,
            details=details or {},
        )
        self._activities.append(entry)
        return entry

    def list_activities(
        self,
        organization_id: str,
        is_admin: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ActivityEntry]:
        """List organization activities respecting administrator audit permissions."""
        filtered = [
            act for act in self._activities
            if act.organization_id == organization_id
        ]
        
        # If not admin, exclude high-privilege or sensitive internal/administrative audit events
        if not is_admin:
            filtered = [
                act for act in filtered
                if not act.action.startswith("ADMIN_") and not act.action.startswith("INTERNAL_")
            ]
        else:
            # Administrators see everything except core internal background system tasks
            filtered = [
                act for act in filtered
                if not act.action.startswith("INTERNAL_")
            ]

        sorted_acts = sorted(filtered, key=lambda x: x.timestamp, reverse=True)
        return sorted_acts[offset:offset + limit]

    def get_dashboard_summary(
        self,
        user_id: str,
        organization_id: str,
        projects: list[dict[str, Any]],
        work_items: list[dict[str, Any]],
        timezone_str: str = "UTC",
    ) -> DashboardSummary:
        """Derive active projects, assigned work, and recent updates for the user dashboard."""
        target_tz = timezone.utc
        if ZoneInfo is not None:
            try:
                target_tz = ZoneInfo(timezone_str)
            except Exception:
                target_tz = timezone.utc

        def _localize_dt(val: Any) -> Any:
            if isinstance(val, datetime):
                if val.tzinfo is None:
                    val = val.replace(tzinfo=timezone.utc)
                return val.astimezone(target_tz)
            return val

        active_projects = []
        for p in projects:
            if p.get("organization_id") == organization_id and p.get("status") not in ("completed", "archived"):
                p_copy = dict(p)
                if "due_date" in p_copy:
                    p_copy["due_date"] = _localize_dt(p_copy["due_date"])
                if "updated_at" in p_copy:
                    p_copy["updated_at"] = _localize_dt(p_copy["updated_at"])
                active_projects.append(p_copy)

        assigned_work = []
        for w in work_items:
            if (
                w.get("organization_id") == organization_id
                and w.get("assignee_id") == user_id
                and w.get("status") not in ("completed", "archived")
            ):
                w_copy = dict(w)
                if "due_date" in w_copy:
                    w_copy["due_date"] = _localize_dt(w_copy["due_date"])
                if "updated_at" in w_copy:
                    w_copy["updated_at"] = _localize_dt(w_copy["updated_at"])
                assigned_work.append(w_copy)

        raw_recently_updated = [
            w for w in work_items
            if w.get("organization_id") == organization_id
            and (w.get("assignee_id") == user_id or w.get("member_involved", False))
        ]

        sorted_recently_updated = sorted(
            raw_recently_updated,
            key=lambda x: x.get("last_meaningful_update", x.get("updated_at", datetime.min)),
            reverse=True,
        )[:10]

        recently_updated = []
        for w in sorted_recently_updated:
            w_copy = dict(w)
            if "last_meaningful_update" in w_copy:
                w_copy["last_meaningful_update"] = _localize_dt(w_copy["last_meaningful_update"])
            if "updated_at" in w_copy:
                w_copy["updated_at"] = _localize_dt(w_copy["updated_at"])
            if "due_date" in w_copy:
                w_copy["due_date"] = _localize_dt(w_copy["due_date"])
            recently_updated.append(w_copy)

        empty_message = None
        if not assigned_work and not active_projects:
            empty_message = "You have no active projects or assigned work items at this time."

        return DashboardSummary(
            organization_id=organization_id,
            user_id=user_id,
            active_projects=active_projects,
            assigned_work_items=assigned_work,
            recently_updated_items=recently_updated,
            empty_state_message=empty_message,
        )