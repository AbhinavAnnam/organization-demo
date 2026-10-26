import uuid
import datetime
import threading
import queue
import logging
from typing import List, Dict, Optional, Any, Callable, Set
from dataclasses import dataclass, field

# ----------------------------------------------------------------------
# Exceptions
# ----------------------------------------------------------------------
class ConcurrentModificationException(Exception):
    """Raised when a concurrent modification or optimistic locking conflict occurs."""
    pass

class DuplicateActionException(Exception):
    """Raised when an action that must happen only once is attempted more than once."""
    pass

class DependencyFailureException(Exception):
    """Raised when an external dependency (search, email, storage) fails."""
    pass

class IdempotencyConflictException(Exception):
    """Raised when an idempotency key is reused with conflicting parameters or states."""
    pass

class JobExecutionException(Exception):
    """Raised when a background job execution fails."""
    pass

class MaxRetriesExceededException(Exception):
    """Raised when a background job exceeds its maximum allowed retry attempts."""
    pass

# ----------------------------------------------------------------------
# Data Models
# ----------------------------------------------------------------------
@dataclass
class BackgroundJob:
    """Represents an asynchronous background job with tenant scoping and idempotency support."""
    job_id: uuid.UUID
    organization_id: uuid.UUID
    task_type: str
    payload: Dict[str, Any]
    idempotency_key: str
    max_retries: int = 3
    retry_count: int = 0
    status: str = "pending"  # pending, running, completed, failed, dead_letter
    created_at: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    last_error: Optional[str] = None

@dataclass
class VersionedWorkItem:
    """Represents a work item supporting optimistic locking version control."""
    work_item_id: uuid.UUID
    organization_id: uuid.UUID
    project_id: uuid.UUID
    title: str
    status: str
    assignee_id: Optional[str]
    version: int = 1
    updated_at: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

# ----------------------------------------------------------------------
# Concurrency & Background Processing Service
# ----------------------------------------------------------------------
class ConcurrencyManager:
    """
    Manages thread safety, optimistic locking for work items, atomic single-execution
    actions (invitation acceptances, ownership transfers), idempotent retry handling,
    and resilient background processing with decoupling from core operations.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # Optimistic locking version store: work_item_id -> VersionedWorkItem
        self._work_items: Dict[uuid.UUID, VersionedWorkItem] = {}
        # Single-action execution registry: action_key -> result/state
        self._executed_actions: Set[str] = set()
        # Idempotency token storage: idempotency_key -> execution result/status
        self._idempotent_store: Dict[str, Any] = {}
        # Background job queue and dead letter queue
        self._job_queue: queue.Queue[BackgroundJob] = queue.Queue()
        self._dead_letter_queue: List[BackgroundJob] = []
        self._worker_active = False
        self._worker_thread: Optional[threading.Thread] = None
        self._job_handlers: Dict[str, Callable[[BackgroundJob], None]] = {}

    def register_job_handler(self, task_type: str, handler: Callable[[BackgroundJob], None]) -> None:
        """Register a handler function for asynchronous background task types."""
        with self._lock:
            self._job_handlers[task_type] = handler

    def start_worker(self) -> None:
        """Start the background worker thread for asynchronous processing."""
        with self._lock:
            if self._worker_active:
                return
            self._worker_active = True
            self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self._worker_thread.start()

    def stop_worker(self) -> None:
        """Stop the background worker thread cleanly."""
        with self._lock:
            self._worker_active = False
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=2.0)

    def _worker_loop(self) -> None:
        """Background worker loop executing tasks with safe retry logic and dead-letter queuing."""
        while True:
            try:
                job = self._job_queue.get(timeout=0.5)
            except queue.Empty:
                with self._lock:
                    if not self._worker_active:
                        break
                continue

            try:
                job.status = "running"
                handler = self._get_handler(job.task_type)
                if handler:
                    handler(job)
                    job.status = "completed"
                else:
                    raise JobExecutionException(f"No handler registered for task type: {job.task_type}")
            except Exception as e:
                job.retry_count += 1
                job.last_error = str(e)
                if job.retry_count >= job.max_retries:
                    job.status = "dead_letter"
                    with self._lock:
                        self._dead_letter_queue.append(job)
                else:
                    job.status = "pending"
                    # Re-queue for retry
                    self._job_queue.put(job)
            finally:
                self._job_queue.task_done()

    def _get_handler(self, task_type: str) -> Optional[Callable[[BackgroundJob], None]]:
        with self._lock:
            return self._job_handlers.get(task_type)

    def enqueue_background_job(
        self,
        organization_id: uuid.UUID,
        task_type: str,
        payload: Dict[str, Any],
        idempotency_key: str,
        max_retries: int = 3,
    ) -> BackgroundJob:
        """Enqueue an asynchronous background task ensuring organization context and idempotency."""
        with self._lock:
            if idempotency_key in self._idempotent_store:
                existing_job = self._idempotent_store[idempotency_key]
                return existing_job

            job = BackgroundJob(
                job_id=uuid.uuid4(),
                organization_id=organization_id,
                task_type=task_type,
                payload=payload,
                idempotency_key=idempotency_key,
                max_retries=max_retries,
            )
            self._idempotent_store[idempotency_key] = job
            self._job_queue.put(job)
            return job

    def execute_once(self, action_key: str, action_func: Callable[[], Any]) -> Any:
        """Ensure an action that must happen only once (e.g., invitation acceptance) executes atomically without duplicates."""
        with self._lock:
            if action_key in self._executed_actions:
                raise DuplicateActionException(f"Action '{action_key}' has already been executed.")
            try:
                result = action_func()
                self._executed_actions.add(action_key)
                return result
            except Exception as exc:
                if isinstance(exc, DuplicateActionException):
                    raise
                raise

    def update_work_item_optimistically(
        self,
        work_item_id: uuid.UUID,
        organization_id: uuid.UUID,
        expected_version: int,
        updater_func: Callable[[VersionedWorkItem], VersionedWorkItem],
    ) -> VersionedWorkItem:
        """Update a work item using optimistic locking to prevent stale views from overwriting concurrent modifications."""
        with self._lock:
            item = self._work_items.get(work_item_id)
            if not item:
                raise ConcurrentModificationException("Work item not found.")
            if item.organization_id != organization_id:
                raise ConcurrentModificationException("Tenant isolation violation.")
            if item.version != expected_version:
                raise ConcurrentModificationException(
                    f"Conflict detected: expected version {expected_version}, but current version is {item.version}."
                )

            updated = updater_func(item)
            updated.version = item.version + 1
            updated.updated_at = datetime.datetime.now(datetime.timezone.utc)
            self._work_items[work_item_id] = updated
            return updated

    def create_work_item(
        self,
        work_item_id: uuid.UUID,
        organization_id: uuid.UUID,
        project_id: uuid.UUID,
        title: str,
        status: str,
        assignee_id: Optional[str] = None,
    ) -> VersionedWorkItem:
        """Register a new work item into the versioned concurrency store."""
        with self._lock:
            item = VersionedWorkItem(
                work_item_id=work_item_id,
                organization_id=organization_id,
                project_id=project_id,
                title=title,
                status=status,
                assignee_id=assignee_id,
                version=1,
            )
            self._work_items[work_item_id] = item
            return item

    def get_work_item(self, work_item_id: uuid.UUID, organization_id: uuid.UUID) -> VersionedWorkItem:
        """Retrieve a versioned work item with tenant isolation checks."""
        with self._lock:
            item = self._work_items.get(work_item_id)
            if not item or item.organization_id != organization_id:
                raise ConcurrentModificationException("Work item not found.")
            return item

    def handle_peripheral_dependency_failure(
        self,
        core_operation: Callable[[], Any],
        peripheral_operation: Callable[[], Any],
        fallback_task_type: str,
        organization_id: uuid.UUID,
        idempotency_key: str,
    ) -> Any:
        """Execute a core operation and attempt a peripheral operation (such as search indexing or email), queueing for async retry if peripheral fails without rolling back core success."""
        core_result = core_operation()
        try:
            peripheral_operation()
        except Exception:
            # Peripheral service failure must not roll back core domain action; queue for background retry
            self.enqueue_background_job(
                organization_id=organization_id,
                task_type=fallback_task_type,
                payload={"idempotency_key": idempotency_key},
                idempotency_key=f"retry_{idempotency_key}",
            )
        return core_result

    def get_dead_letter_jobs(self) -> List[BackgroundJob]:
        """Retrieve permanently failed jobs for operator visibility and tooling inspection."""
        with self._lock:
            return list(self._dead_letter_queue)