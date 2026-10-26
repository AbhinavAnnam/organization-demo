# Northstar — change report

Run: `e40803e5-fc43-4be1-8dae-b7e812593ffa`
Candidate: `0a485429c5b4672b7bd4015f8825a73878ae4fbfa262ced31b58fef243cacb94`

## Change summary

256 requirements assessed; 0 confirmed defects, 3 uncertain findings, 0 suggestions.

Critic verdict: **needs_review**. 256 requirements assessed.
Coverage: met: 205, partial: 0, missing: 0, unclear: 51.
Findings: 0 confirmed defects, 3 uncertain findings, 0 suggestions.

Repository: https://github.com/AbhinavAnnam/organization-demo.git
Base branch: `main`
Baseline commit: `ef2fc24cc789201d28219585002a853b84570597`
Working branch: `ai-native/c9ec1c830c8149e98e42657908721df4`

## Files and modifications

| File | Change | Lines added | Lines removed |
| --- | --- | ---: | ---: |
| src/organization_demo/accounts_identity.py | modified | 341 | 48 |
| src/organization_demo/administration.py | added | 318 | 0 |
| src/organization_demo/concurrency.py | added | 269 | 0 |
| src/organization_demo/notifications_management.py | modified | 15 | 3 |
| src/organization_demo/search_service.py | modified | 150 | 97 |
| src/organization_demo/work_item_management.py | added | 850 | 0 |

### src/organization_demo/accounts_identity.py

- AccountsIdentityDirectory: changed
- CannotRemoveLastProjectOwnerException: added
- DuplicateOrganizationIdentifierException: added
- EmailAlreadyExistsException: added
- InsufficientPermissionException: added
- InvalidPasswordResetTokenException: added
- InvalidProjectOwnerTransferException: added
- InvalidSettingValueException: added
- NonOrganizationMemberProjectAddException: added
- Project: added
- ProjectDeletionBlockedException: added
- ProjectMemberNotFoundException: added
- ProjectMembership: changed
- ProjectNotFoundException: added
- SelfRoleElevationException: added
- SettingNotFoundException: added
- UnauthorizedOrganizationAccessException: added
- UnverifiedAccountException: added

### src/organization_demo/administration.py

- AdminAuthorizationException: added
- AdministrationService: added
- AuthorizationError: added
- DestructiveActionConfirmationRequiredException: added
- InternalServerError: added
- InvalidOwnerAssignmentException: added
- MemberInfo: added
- OrganizationContext: added
- OrganizationSettings: added
- OwnerNotFoundException: added
- ParentAccessDeniedException: added
- ValidationError: added

### src/organization_demo/concurrency.py

- BackgroundJob: added
- ConcurrencyManager: added
- ConcurrentModificationException: added
- DependencyFailureException: added
- DuplicateActionException: added
- IdempotencyConflictException: added
- JobExecutionException: added
- MaxRetriesExceededException: added
- VersionedWorkItem: added

### src/organization_demo/notifications_management.py

- EmailSendException: added
- NotificationNotFoundException: added
- NotificationService: changed
- TemplateNotFoundException: added

### src/organization_demo/search_service.py

- ActivityEntry: changed
- ActivityLogPersistenceException: added
- DashboardRenderException: added
- SearchIndexUnavailableException: added
- SearchQueryMalformedException: added
- SearchService: changed
- TimezoneParseException: added
- compute_relative_time_label: changed

### src/organization_demo/work_item_management.py

- Attachment: added
- AttachmentNotFoundException: added
- Comment: added
- CommentModerationException: added
- CommentNotFoundException: added
- CrossTenantAccessException: added
- FileSizeExceededException: added
- FileSizeLimitExceededException: added
- InvalidAssigneeException: added
- InvalidFilenameException: added
- InvalidPathException: added
- InvalidStatusTransitionException: added
- MalformedIdentifierException: added
- StorageBackendException: added
- StorageUnavailableException: added
- UnauthorizedAccessException: added
- UnauthorizedCommentEditException: added
- WorkItem: added
- WorkItemDueDate: added
- WorkItemManagementService: added
- WorkItemNotFoundException: added

## Validation and testing

- Approved Python files were checked for valid syntax and matched to the reviewed candidate.
- **Automated tests were not run in this delivery workflow. The testing phase was skipped.**
- The critic is a static, model-assisted assessment; its verdict does not establish runtime correctness.
- Remaining findings are disclosed below for the pull request reviewer.

## Requirement coverage

| Requirement | Module | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| R-3efde51f8a16 | accounts_and_identity | User accounts are identified primarily by email address, but email address is not used as an organization identity for authorization purposes. | met | Account identified by email |
| R-50a99b7b3238 | accounts_and_identity | A single user account can belong to multiple organizations without creating separate accounts. | met | Single account multiple orgs |
| R-f4d700a2ad2c | accounts_and_identity | Registration requires email address and password, followed by email ownership verification. Unverified accounts cannot be fully active. | met | Verification required for active |
| R-b7e00795f6d7 | accounts_and_identity | Email address lookup must be case-insensitive, while preserving the user's originally supplied capitalization for display. | met | Email case-insensitive lookup |
| R-0217465739bd | accounts_and_identity | Password reset requests must be accessible from the sign-in page without an authenticated session. | met | Request reset without session |
| R-eaaadc2d11f5 | accounts_and_identity | Password reset mechanism must not disclose whether an email address exists in the system to prevent user enumeration. | met | Reset request returns None |
| R-3a35b9851f97 | accounts_and_identity | Password reset links must be temporary and single-use; a reset link becomes invalid after successful reset. | met | Single-use reset token cleared |
| R-3a9680492b9e | accounts_and_identity | Password change must invalidate all active sessions issued prior to the change. | met | Invalidate prior sessions |
| R-767ce1af539f | accounts_and_identity | Users can edit their own profile display name, which is not forced to equal their email address. | met | Update profile display name |
| R-28e883e958c4 | accounts_and_identity | Account deactivation by a user must preserve historical references to the user across all associated organizations. | met | Preserve historical references |
| R-69ff90c0feae | accounts_and_identity | The user who creates an organization becomes its initial owner. | met | Creator becomes owner |
| R-5af7729f7fbe | accounts_and_identity | An organization has a display name (non-unique) and an optional short identifier for URLs and integrations that must be unique to prevent ambiguous routing. | met | Unique slug for URLs |
| R-9651b71fad4e | accounts_and_identity | Organizations are strictly isolated boundaries; membership in Organization A grants no access to Organization B. | met | Strict isolated boundaries |
| R-9c3fde1cec35 | accounts_and_identity | Organization owners can invite users via email address. If the invitee has an existing account, accepting adds the existing account to the organization; if not, it triggers registration. | met | Invite user by email |
| R-9521b57ac197 | accounts_and_identity | Invitations must expire after a configurable duration and can be explicitly revoked by an administrator prior to acceptance. | met | Expiration and revocation |
| R-103d9264dfb8 | accounts_and_identity | Accepting an invitation to one organization does not consume or invalidate invitations from other organizations. | met | Accepting does not consume other |
| R-cccb43bb118b | accounts_and_identity | Organization names can be modified without altering historical activity logs. | met | Names modified without logs |
| R-989f6486f70e | accounts_and_identity | Organization administrators can configure workspace behavior, primarily organization name and timezone. | met | Configure workspace settings |
| R-9562bd37d860 | accounts_and_identity | Settings must be scoped to the organization rather than global user preferences. | met | Settings scoped to org |
| R-333dfb9d9fa9 | accounts_and_identity | Changing an organization's timezone affects future displays of dates and times, but must not rewrite original timestamps of existing activities. | met | Timezone change future display |
| R-bc40d19770d9 | accounts_and_identity | Settings changes may be recorded in administrative activity. | met | Audit log for settings |
| R-7126014d1c05 | accounts_and_identity | An organization should retain sensible defaults when settings are unconfigured, distinguishing absent optional configuration from deliberately selected defaults. | met | Explicit user-set tracking |
| R-10188882e683 | accounts_and_identity | The role model supports three levels: Owner (organization-level control, ownership transfer), Administrator (operational management), and Member (project participant). | met | Three role levels |
| R-a9444668e77e | accounts_and_identity | Authorization checks must be performed on the server side for every request. | met | Server-side authorization check |
| R-2d9641d70822 | accounts_and_identity | Removing a member immediately revokes access to organization data via authenticated requests. | met | Revokes access immediately |
| R-451b37e224d6 | accounts_and_identity | Member removal does not delete or overwrite historical activity records, comments, or past assignment records generated by that user. | met | Preserves audit history |
| R-c1509c884284 | accounts_and_identity | Administrators can change member roles, but members cannot elevate their own permissions or modify owner permissions. | met | Prevent self role elevation |
| R-04e3a14d3dd6 | accounts_and_identity | The organization member listing must clearly distinguish active members from pending invitations. | met | Distinguish active and pending |
| R-af8921148442 | accounts_and_identity | Projects belong to an organization and contain a name, description, creator, owner, status, timestamps, and project membership. | met | Project fields defined |
| R-6abe08fd69dd | accounts_and_identity | Project access is distinct from organization membership; only organization members can be added to projects. | met | Only org members in project |
| R-53c97f9bcf5f | accounts_and_identity | The creator of a project becomes its initial project owner upon creation. | met | Creator initial owner |
| R-2a4db379a63a | accounts_and_identity | Project owners and organization administrators can add or remove project members. | met | Add or remove project members |
| R-b68f7a501f08 | accounts_and_identity | Completed projects represent concluded work; archiving a project removes it from active views while preserving inspectability for authorized users. | met | Archive project status |
| R-41a33b6e9c42 | accounts_and_identity | Project names do not require global or organization-wide uniqueness. | met | Project name uniqueness |
| R-d0a9ca9cb065 | accounts_and_identity | Deleting a project is a destructive action requiring cascading cleanup of dependent work items, comments, attachments, and activity records to prevent orphaned data. | met | Delete project and cleanup |
| R-8363de0ee64b | accounts_and_identity | Project descriptions support standard formatting but must be rendered as non-executable text. | met | Project description field |
| R-b02c4245902f | accounts_and_identity | Projects optionally support a due date; no default due date is assigned upon creation. | met | Optional due date |
| R-3f9f40bb07d8 | accounts_and_identity | Project membership determines which organization members can participate in a project. | met | Project membership check |
| R-6ea92e7826d4 | accounts_and_identity | Removing a project member revokes access to project-restricted data without automatically reassigning or deleting work items assigned to that member. | met | Removing member revokes access |
| R-e4431fb88ece | accounts_and_identity | Comments and activity recorded by a removed project member remain part of project history. | met | History preserved on removal |
| R-58708c15181d | accounts_and_identity | A project owner cannot be removed from a project unless another project owner is designated. | met | Cannot remove last project owner |
| R-f7781e512337 | accounts_and_identity | InvalidCredentialsException | met | InvalidCredentialsException defined |
| R-e70fcc28f2c3 | accounts_and_identity | UnverifiedAccountException | met | UnverifiedAccountException defined |
| R-f74f0d8fdb56 | accounts_and_identity | InvalidPasswordResetTokenException | met | InvalidPasswordResetTokenException |
| R-7c4637f05a58 | accounts_and_identity | EmailAlreadyExistsException | met | EmailAlreadyExistsException |
| R-c95a4a16e2e9 | accounts_and_identity | OrganizationNotFoundException | met | OrganizationNotFoundException |
| R-a205534bc674 | accounts_and_identity | DuplicateOrganizationIdentifierException | met | DuplicateOrganizationIdentifierException |
| R-aac7b6b41874 | accounts_and_identity | InvitationExpiredException | met | InvitationExpiredException |
| R-24db26db485d | accounts_and_identity | InvitationRevokedException | met | InvitationRevokedException |
| R-48144aa9a5c5 | accounts_and_identity | UnauthorizedOrganizationAccessException | met | UnauthorizedOrganizationAccessException |
| R-5a00aa6cf8e2 | accounts_and_identity | SettingNotFoundException | met | SettingNotFoundException |
| R-29be98ac4f49 | accounts_and_identity | InvalidSettingValueException | met | InvalidSettingValueException |
| R-fbd7eb3c288b | accounts_and_identity | InsufficientPermissionException | met | InsufficientPermissionException |
| R-9cca72f82099 | accounts_and_identity | MemberNotFoundException | met | MemberNotFoundException |
| R-4af71436068a | accounts_and_identity | SelfRoleElevationException | met | SelfRoleElevationException |
| R-2824b836a7b7 | accounts_and_identity | OwnerRemovalException | met | OwnerRemovalException |
| R-e1017ac8e7d0 | accounts_and_identity | ProjectNotFoundException | met | ProjectNotFoundException |
| R-2a8509e0307f | accounts_and_identity | InvalidProjectOwnerTransferException | met | InvalidProjectOwnerTransferException |
| R-210ae5827a45 | accounts_and_identity | ProjectDeletionBlockedException | met | ProjectDeletionBlockedException |
| R-2e0b92cacb56 | accounts_and_identity | NonOrganizationMemberProjectAddException | met | NonOrganizationMemberProjectAddException |
| R-ee4c09b669b0 | accounts_and_identity | ProjectMemberNotFoundException | met | ProjectMemberNotFoundException |
| R-b3dbca485700 | accounts_and_identity | CannotRemoveLastProjectOwnerException | met | CannotRemoveLastProjectOwnerException |
| R-d69f34c4b36b | work_item_management | A work item belongs to one project and requires at minimum a title and status. | met | WorkItem dataclass defines title and status. |
| R-8fc4782900ce | work_item_management | Description, priority, creator, assignee, timestamps, and due date are optional fields. | met | Optional fields configured with Optional type hints. |
| R-6c82baea4ce1 | work_item_management | Initial workflow statuses are limited to Not Started, In Progress, and Completed. | met | VALID_STATUSES defined with exact three statuses. |
| R-871577d1bb9e | work_item_management | Work items are mutable after completion and can transition backward from Completed to active statuses. | met | update_work_item allows transitioning back from Completed. |
| R-d9503cb19522 | work_item_management | Priority is represented using an ordered range with explicit human-readable semantics rather than raw numeric codes. | met | Priority stored as human-readable string values. |
| R-ba582bfbc9ba | work_item_management | Only project members can be assigned to a work item. Unassigned work items are valid. | met | Assignee checked against project members. |
| R-e47537617bad | work_item_management | If an assignee is removed from a project, existing work item assignments remain intact as historical records. | met | Assignments remain intact in historical records. |
| R-a205faac8611 | work_item_management | Work item due dates are date-only calendar values independent of viewer timezones, and the system must distinguish between an absent due date and a due date set to today. | met | WorkItemDueDate uses date-only calendar values. |
| R-11752ef52d82 | work_item_management | Work items can be manually reordered within project views for display preference without altering business priority. | met | reorder_work_item updates display_order field. |
| R-d8574e47718e | work_item_management | Work item updates (title, status, assignee, description, due date removal) must create corresponding activity history logs. | met | Changes append corresponding activity history logs. |
| R-45ad7f075d97 | work_item_management | API requests with malformed identifiers or invalid state values must be rejected. | met | _validate_identifier rejects malformed UUIDs. |
| R-4afa2c416416 | work_item_management | Cross-tenant requests targeting work items in another organization must return unauthorized or unavailable responses without exposing resource existence. | met | get_work_item raises CrossTenantAccessException. |
| R-33855168a26e | work_item_management | Comments are attached directly to work items in a linear structure without nested replies. | met | Comment dataclass stores list of comments directly. |
| R-306c7db6035b | work_item_management | A comment contains an author, body text, creation timestamp, and edited state flag. | met | Comment dataclass contains author, body, timestamp. |
| R-738033640797 | work_item_management | Users can edit their own comments. Author and creation timestamp must be preserved upon editing. | met | edit_comment preserves author and creation timestamp. |
| R-2e407ab0b518 | work_item_management | Organization administrators can moderate or delete comments in exceptional circumstances. | met | is_admin parameter allows editing/deleting. |
| R-4864ef74d3a1 | work_item_management | Deleting a comment must retain a tombstone or deletion indicator in historical activity rather than purging the record trace. | met | delete_comment retains tombstone comment record. |
| R-135c25f0d74c | work_item_management | Comment content must be treated as untrusted input and properly sanitized or escaped to prevent code execution (XSS). | unclear | render_comment_content provided but not applied on add. |
| R-e9604fff579d | work_item_management | Attachments can be uploaded to a work item or associated with a specific comment. | met | add_attachment accepts comment_id association. |
| R-a552ca58e315 | work_item_management | File storage mechanism must be decoupled from application servers. | met | Attachment storage_id uses opaque decoupled keys. |
| R-43fb6b39ead0 | work_item_management | File upload size must be strictly limited; oversized files must be rejected. | met | MAX_FILE_SIZE_BYTES limits upload sizes. |
| R-d39569c36ec9 | work_item_management | User-provided filenames must be sanitized and treated as untrusted data to prevent path traversal attacks. | met | _contains_path_traversal and sanitize_filename. |
| R-12c73a9dd034 | work_item_management | Duplicate filenames are permitted and must be differentiated via unique internal storage keys. | met | storage_id includes unique random hex string. |
| R-b21acc283e52 | work_item_management | Deleting an attachment revokes normal file access and leaves an activity record without retaining a publicly accessible file copy. | met | delete_attachment sets deleted flag and removes item. |
| R-1ea6df32dabc | work_item_management | Attachments may be uploaded directly to a work item and associated with an individual comment. | met | add_attachment supports comment association. |
| R-30d56b9e20cf | work_item_management | File storage mechanism is an implementation concern and must not assume content belongs on the same server as the application. | met | storage_id uses opaque unique identifier. |
| R-261d4d612076 | work_item_management | Enforce reasonable limits around uploaded content; extremely large files must be rejected rather than allowed to consume unlimited storage. | met | MAX_FILE_SIZE_BYTES limits large file uploads. |
| R-6a873fcaf4d3 | work_item_management | File names supplied by users must not be trusted as filesystem paths or direct filesystem locations. | met | sanitize_filename secures user-provided filenames. |
| R-bbac109d6abe | work_item_management | Two files may have the same display name without representing the same attachment. | met | Storage keys differentiate duplicate filenames. |
| R-3a90c6b3ae63 | work_item_management | Deleting an attachment removes it from normal access, while historical activity can indicate removal without retaining a publicly accessible copy. | met | delete_attachment revokes file access. |
| R-ebfb36b5f889 | work_item_management | An attachment belonging to a work item must follow the access rules of that work item. | met | get_attachment enforces project membership rules. |
| R-b88e2b31337e | work_item_management | Knowing a storage identifier must not be sufficient to retrieve a private file. | met | get_attachment verifies membership and work item ID. |
| R-bb39575eab7e | work_item_management | Downloads must be authorized independently from the page that displays the work item. | met | get_attachment method operates independently. |
| R-e008034aef1b | work_item_management | Unsupported formats may be offered as downloadable content without inline preview. | unclear | No explicit rendering download protocol shown. |
| R-9c996b587d58 | work_item_management | Uploaded files are untrusted and file content must not automatically be interpreted as HTML or executable code. | unclear | sanitize_filename strips tags, but content not restricted. |
| R-7b29ebced5f2 | work_item_management | Use appropriate content-disposition behavior for downloads where inline rendering introduces security concerns. | unclear | Content-disposition headers require UI/HTTP layer. |
| R-fcfc8f994ce6 | work_item_management | Authentication and authorization must be applied before generating or serving private file access. | met | get_attachment validates membership before access. |
| R-3634e19d14be | work_item_management | Temporary file-access mechanisms must have a limited lifetime. | unclear | Temporary access lifetime logic is not present. |
| R-652d652821d9 | work_item_management | File upload limits must be enforced before allowing unbounded data transfer. | met | size_bytes checked before storing attachments. |
| R-69346b98780f | work_item_management | The system must handle two users uploading files with identical names such that one file may be replaced while another remains valid. | met | storage_id uses unique uuid hex for each upload. |
| R-c5799c21e46c | work_item_management | WorkItemNotFoundException | met | WorkItemNotFoundException defined. |
| R-b630c81dd622 | work_item_management | InvalidStatusTransitionException | met | InvalidStatusTransitionException defined. |
| R-427bc6315373 | work_item_management | InvalidAssigneeException | met | InvalidAssigneeException defined. |
| R-c5c4b9784b37 | work_item_management | MalformedIdentifierException | met | MalformedIdentifierException defined. |
| R-96c2abff40cb | work_item_management | CrossTenantAccessException | met | CrossTenantAccessException defined. |
| R-736ca237a7e5 | work_item_management | CommentNotFoundException | met | CommentNotFoundException defined. |
| R-f537de645ce1 | work_item_management | UnauthorizedCommentEditException | met | UnauthorizedCommentEditException defined. |
| R-ee9bbbc0bfba | work_item_management | CommentModerationException | met | CommentModerationException defined. |
| R-d613b2558bf8 | work_item_management | AttachmentNotFoundException | met | AttachmentNotFoundException defined. |
| R-8840449ac38e | work_item_management | FileSizeLimitExceededException | met | FileSizeLimitExceededException defined. |
| R-69af0bc78fdc | work_item_management | InvalidFilenameException | met | InvalidFilenameException defined. |
| R-43b20a726378 | work_item_management | StorageBackendException | met | StorageBackendException defined. |
| R-ddab1d750665 | work_item_management | StorageUnavailableException | met | StorageUnavailableException defined. |
| R-84f67338b7b3 | work_item_management | FileSizeExceededException | met | FileSizeExceededException defined. |
| R-64aff9a4ccc3 | work_item_management | InvalidPathException | met | InvalidPathException defined. |
| R-9e1369029405 | work_item_management | UnauthorizedAccessException | met | UnauthorizedAccessException defined. |
| R-f412a59e27a6 | notifications | Northstar should notify people when something relevant happens to their work to prevent repeatedly inspecting every project. | met | NotificationService generates notifications for relevant work events. |
| R-8c0cd29dd64e | notifications | Being assigned a work item or mentioned in a comment is notification-worthy. | met | WORK_ITEM_ASSIGNED and COMMENT_MENTION enum values implemented. |
| R-7c43d538be1f | notifications | A comment on an item actively followed by a person may generate a notification depending on their notification settings. | met | COMMENT_ON_FOLLOWED_ITEM checks email settings. |
| R-0268ba21e877 | notifications | Internal bookkeeping changes with no user-facing significance must remain invisible. | met | Internal metrics and bookkeeping use private attributes. |
| R-293385d63b6f | notifications | Notifications must identify the event sufficiently for a user to understand why it appeared. | met | Notification includes event_type, message, and related_id. |
| R-853252bf88a8 | notifications | A notification can be marked as read without deleting it, and the list must distinguish unread items from previously viewed ones. | met | mark_as_read updates read_at; list_notifications orders unread first. |
| R-de5092261abe | notifications | Users may have preferences controlling certain categories of notification. | met | set_email_notifications_enabled controls user preferences. |
| R-630d2196fe57 | notifications | Disabling an email notification must not be interpreted as disabling the underlying event or removing an in-app notification unless explicitly defined as the same preference. | met | Disabling email does not delete in-app notifications. |
| R-c2fbc7e584fe | notifications | Email delivery may fail independently; a failed email must not cause the underlying assignment or mention to be rolled back. | met | Async email execution catches exceptions independently. |
| R-4e42a8a72337 | notifications | The system must avoid producing duplicate notifications when the same operation is retried. | met | _generated_keys prevents duplicate notification creation. |
| R-fe979c1027fd | notifications | Transactional email is used for account verification, password recovery, invitations, and selected notifications. | met | send_invitation handles transactional invitation emails. |
| R-0f9581bd4139 | notifications | Emails contain links back to Northstar containing temporary credentials or tokens rather than exposing passwords. | met | Email templates support placeholders like token. |
| R-1bba5e3e7961 | notifications | Email templates may be updated independently of the main application logic. | met | EmailTemplate is independent container class. |
| R-86fa61c7d4e8 | notifications | The application should not assume email delivery is instantaneous; an invitation may remain pending while the mail provider experiences delays. | met | Async background worker handles retries with backoff delays. |
| R-2b9e5521541c | notifications | Email sending should occur asynchronously where practical. | met | _dispatch_email_async spawns a background thread. |
| R-1b497d83357f | notifications | Email addresses should not be logged unnecessarily in broadly accessible operational logs. | met | _mask_email prevents logging raw personal PII. |
| R-2b8d400211bc | notifications | The system must distinguish between an action that successfully created an invitation and an attempt to deliver the associated email. | met | send_invitation adds notification and separate async dispatch. |
| R-6ef5f9e8775d | notifications | NotificationDeliveryException | met | NotificationDeliveryException defined. |
| R-8ec78cb3799c | notifications | NotificationNotFoundException | met | NotificationNotFoundException defined. |
| R-8c4bc5fb507b | notifications | EmailSendException | met | EmailSendException defined. |
| R-13a305ac721c | notifications | TemplateNotFoundException | met | TemplateNotFoundException defined. |
| R-dc71fa69b000 | search | Search spans accessible operational content and must respect organization and project access boundaries. | met | Enforces organization_id, project access set, and allowed_user_ids. |
| R-a7831a10e8af | search | Search is not an exception to authorization; a user searching for a phrase must not discover a project they cannot open. | met | Validates user access permissions during document matching. |
| R-3126b476ca61 | search | Initial search focuses on project names, descriptions, work item titles, descriptions, and comments. | met | Searches title, description, content, and comments. |
| R-04932a398dc3 | search | Search results should provide enough surrounding context to recognize why a result was returned. | met | Generates a truncated snippet with context around matches. |
| R-7087d32ba8ad | search | Search is not expected to understand natural-language questions in the first release, favoring useful partial matching. | met | Performs case-insensitive partial matching. |
| R-45046d5cec3f | search | Search indexing may not be instantaneous; newly created items take a short period before appearing. | met | Indexing is synchronous/asynchronous logic without instant constraints. |
| R-a2971b533557 | search | Deleting or restricting an object should eventually remove it from search results for users who no longer have access. | met | remove_document removes items from the index. |
| R-c09aeacea631 | search | Search ranking is not treated as a contractual ordering; clients should not depend on one exact ranking algorithm. | met | Results sorted by deterministic item_type and item_id keys. |
| R-2c699e9d1f32 | search | The dashboard summarizes active projects and work assigned to the current user, answering 'What needs my attention?' | met | Derives active projects and assigned work items. |
| R-86710d3ac9e0 | search | Completed and archived work should not dominate the default dashboard. | met | Filters out completed and archived work items and projects. |
| R-7e30c4067e33 | search | A user with no assigned work should receive a useful empty state rather than a technical error. | met | Sets empty_state_message if assigned_work and active_projects are empty. |
| R-26d715b9828f | search | Recently updated items refer to meaningful user-facing changes, not every database timestamp modification. | met | Sorts recently updated items using last_meaningful_update or updated_at. |
| R-831b452d8d63 | search | The organization timezone must be considered when presenting date-oriented information. | met | Localizes datetime fields with the requested target timezone. |
| R-bfc34d0cbec7 | search | Dashboard counts must be derived from current accessible data rather than being permanently trusted as independent truth. | met | Dashboard lists are derived from provided projects and work items. |
| R-e5d69b2d855c | search | If an item is removed or inaccessible, the dashboard should eventually reflect that as a convenience view. | met | Dashboard excludes completed and archived items. |
| R-159790c1aec0 | search | Records significant activities such as project creation, ownership changes, membership changes, work item creation, assignment/status changes, and administrative actions. | met | record_activity accepts action, actor, and target details. |
| R-054746141b0c | search | Activity should include the actor where an identifiable actor exists; system-generated activities may have no human actor. | met | ActivityEntry stores actor_id and actor_name optionally. |
| R-e7e02f77c1fd | search | Activities must contain timestamps that can be interpreted consistently. | met | ActivityEntry records timestamp with UTC timezone. |
| R-09b85cd16b7c | search | The activity feed does not record internal database operations like search index updates, cache refreshes, or email retries. | met | Blocks actions starting with INTERNAL_, CACHE_, or EMAIL_. |
| R-5ae7234a2cdb | search | Historical information should remain intelligible if the display name of the actor changes later. | met | Stores actor_name as a snapshot string. |
| R-b53d42e0ce22 | search | If a user is deactivated or removed, historical activity continues to refer to the identity without granting new access. | met | Activity records are immutable via __setattr__. |
| R-92fbd5ae27c2 | search | Activity records are append-oriented; ordinary users cannot rewrite history by modifying current objects. | met | ActivityLogImmutableException raised on modification attempts. |
| R-9c9bc7cd427f | search | Administrators may have broader access to activity information than ordinary project participants. | met | list_activities filters based on is_admin flag. |
| R-80279cc1947a | search | Timestamps representing events must have an unambiguous timezone interpretation. | met | Timestamps are explicitly created with timezone.utc. |
| R-33e479ada2cc | search | The organization has a configured timezone for calendar displays, and viewing from another timezone must not store events as a different moment. | met | Timezone localization correctly converts datetimes. |
| R-7547542cb55e | search | Work-item due dates are associated with a calendar day rather than an exact instant, preventing shifts across travel or local clock differences. | met | compute_relative_time_label computes dates dynamically. |
| R-821e33edc99c | search | Relative labels like 'today' and 'tomorrow' must be generated using user or organization context rather than being permanently stored as text. | met | compute_relative_time_label relies on timedelta day differences. |
| R-2cc401cd434a | search | Daylight-saving transitions must not cause date-based logic to assume every calendar day has the exact same number of hours. | unclear | Daylight-saving hour shifts are not explicitly handled. |
| R-e41ef1c12980 | search | SearchIndexUnavailableException | met | SearchIndexUnavailableException defined and raised. |
| R-11c0a674a4b1 | search | SearchQueryMalformedException | met | SearchQueryMalformedException defined and raised. |
| R-8c20a1b9e4d1 | search | DashboardRenderException | met | DashboardRenderException defined and raised. |
| R-434f1ac6cd8a | search | ActivityLogPersistenceException | met | ActivityLogPersistenceException defined and raised. |
| R-112a9fe0b4ba | search | TimezoneParseException | met | TimezoneParseException defined and raised. |
| R-69fb3aacebc5 | administration | Provides organization-level controls including membership management, pending invitations, organization settings, and security information. | met | AdministrationService manages membership, invitations, and settings. |
| R-82ec8f93b0e0 | administration | Administrators must be able to inspect current members and roles, while the owner has additional controls around lifecycle and ownership. | met | verify_admin_privileges and verify_owner_privileges enforce inspection and owner controls. |
| R-a70d53515b8a | administration | Administrative pages must not be accessible simply by knowing their URL. | unclear | URL routing and endpoint protection layer not supplied. |
| R-e3c04de6c929 | administration | An administrator who loses privileges during a session must not continue performing administrative operations indefinitely via an open page. | unclear | Session lifecycle and privilege revocation checks require web layer integration. |
| R-51b8dc84e0cb | administration | Sensitive or destructive operations (removing members, deleting projects, transferring ownership) require additional confirmation to feel deliberate. | met | DestructiveActionConfirmationRequiredException used on remove and transfer. |
| R-825b87d3cdb4 | administration | The interface should make it difficult to mistake 'remove from project' for 'remove from organization'. | unclear | UI distinction between remove from project and organization not supplied. |
| R-d524a9f4daa2 | administration | A current owner may designate another active organization member as owner; the recipient must already belong to the organization. | met | transfer_ownership verifies active member status. |
| R-c6e00b3a8478 | administration | Ownership transfer changes organizational responsibility without creating a second organization. | met | transfer_ownership updates context.owner_id. |
| R-645c86218134 | administration | The previous owner may remain an administrator or member based on selected roles. | met | new_previous_owner_role parameter controls previous owner role. |
| R-95991afa61bc | administration | The operation must be recorded for audit and historical establishment. | unclear | Audit logging recording mechanism not supplied in code. |
| R-0a8cb7ea4a5f | administration | A removed or deactivated account must not leave the organization permanently ownerless if recovery procedures exist. | met | recover_owner_emergency restores active owner. |
| R-d5f62a249698 | administration | Recovery procedures may require elevated operational access and are not ordinary workflows. | met | recover_owner_emergency handles elevated operational access token. |
| R-bda6e859f230 | administration | Visibility follows a layered model: organization membership determines tenant access, projects restrict further, and work items inherit project visibility. | met | verify_data_visibility implements layered checks. |
| R-e9c8e6d87ee6 | administration | Comments and attachments follow the visibility of their parent object to prevent separate authorization rule implementations. | unclear | Comments and attachments source not supplied. |
| R-12cc2793439a | administration | API endpoints returning comments must verify access to the parent work item. | unclear | Comment API endpoints not supplied. |
| R-548e09ab9107 | administration | Downloading an attachment must not bypass project membership checks. | unclear | Attachment download endpoint not supplied. |
| R-dc7a99795372 | administration | Public sharing links are not part of the initial release; unauthenticated users cannot access private projects via forwarded URLs. | unclear | Public sharing link features not supplied. |
| R-20097b40d5d8 | administration | The API should use resource identifiers safe to expose to clients, and authorization must never depend on the difficulty of guessing an identifier. | met | UUID resource identifiers are used. |
| R-a2cfa478cb22 | administration | Validation errors must be distinguishable from authorization failures and server failures. | met | Explicit ValidationError, AuthorizationError, and AdminAuthorizationException raised. |
| R-c0c03d951efd | administration | Malformed requests must not produce internal stack traces or implementation details in normal responses. | met | Custom exceptions prevent internal stack trace leakage. |
| R-65ddece2e604 | administration | Client code should not depend on undocumented database fields as the API evolves. | unclear | Client API response schemas not supplied. |
| R-4bbe0fe901f8 | administration | Modifying operations should return enough information for clients to update local views without reloading every page. | met | list_members_paginated provides stable pagination. |
| R-2f6f8527a206 | administration | Pagination is required for collections (members, projects, notifications, search results, activity feeds) with stable ordering to prevent skipped or repeated records. | unclear | invite_member supports idempotency key check but lacks metadata/notification deduplication. |
| R-100c7d3da11d | administration | Retried operations must avoid creating duplicate logical records for invitations, notifications, and file metadata. | unclear | Idempotency key parameter is accepted in invite_member but unused for full retried operations. |
| R-d8a86e051151 | administration | AdminAuthorizationException | met | AdminAuthorizationException defined. |
| R-35c397780d56 | administration | DestructiveActionConfirmationRequiredException | met | DestructiveActionConfirmationRequiredException defined. |
| R-7c497f2a6e43 | administration | InvalidOwnerAssignmentException | met | InvalidOwnerAssignmentException defined. |
| R-df57b455586c | administration | OwnerNotFoundException | met | OwnerNotFoundException defined. |
| R-69387d2b9194 | administration | ParentAccessDeniedException | met | ParentAccessDeniedException defined. |
| R-db7ad49db6b8 | administration | ValidationError | met | ValidationError defined. |
| R-bb21c8fda030 | administration | AuthorizationError | met | AuthorizationError defined. |
| R-12b7a15808d3 | administration | InternalServerError | met | InternalServerError defined. |
| R-e5fb61fb665c | concurrency | The application should tolerate simultaneous editing of different aspects of the same work item without data corruption. | met | Implemented via update_work_item_optimistically using versions |
| R-7f822e6c284f | concurrency | Stale information views should not unknowingly overwrite newer changes where distinction matters. | met | Version check prevents overwriting newer changes |
| R-171d58ddc38d | concurrency | Simple fields may use last-write behavior, but operations like membership changes and ownership transfers require stronger guarantees. | met | execute_once provides strict execution guarantees |
| R-b5a016fea7af | concurrency | Actions that must happen only once (e.g., invitation acceptance, ownership transfer) must not result in invalid states or duplicate memberships on concurrent submission. | met | execute_once guards against duplicate execution |
| R-bfcd2681eaa4 | concurrency | Retries from clients and infrastructure are expected and treated as normal behavior. | met | BackgroundJob supports retry counts and mechanisms |
| R-d57c9bc25beb | concurrency | The application assumes dependencies (email providers, object storage, databases, search indexing) occasionally fail without rolling back unrelated core operations. | met | Peripheral failures queue background retry without rollback |
| R-0a22568dfc4c | concurrency | Work item creation must not fail if search indexing is temporarily unavailable, provided it can be indexed later. | met | Peripheral failure handler queues background job |
| R-d83b4a3e0e28 | concurrency | Notification delivery problems must not undo successful assignments. | met | core_operation succeeds regardless of peripheral failures |
| R-547fd1d12491 | concurrency | Background processing must be capable of retrying operations safely using idempotency mechanisms or checks on original execution success. | met | Worker loop supports safe retry logic |
| R-187b10a3feba | concurrency | Email sending, search index updates, notification generation, and file processing are handled asynchronously. | met | Background jobs process asynchronously via worker thread |
| R-aa57e47a34dc | concurrency | The UI should distinguish between a completed primary operation and background processing where required (e.g., uploaded file processing state). | unclear | UI layer is not supplied |
| R-e0e6362067f4 | concurrency | Background jobs must contain enough information to identify their target organization and resource without relying on browser sessions. | met | BackgroundJob includes organization_id scoping |
| R-e336f8a219c5 | concurrency | Jobs may be retried, but repeatedly failing jobs must not retry forever without operator visibility and tooling for investigation. | met | Dead letter queue tracks permanently failed jobs |
| R-82f84e6bffbb | concurrency | ConcurrentModificationException | met | Exception class defined |
| R-fc36ea8cbe32 | concurrency | DuplicateActionException | met | Exception class defined |
| R-831bcfcbb733 | concurrency | DependencyFailureException | met | Exception class defined |
| R-ba852d57a3d7 | concurrency | IdempotencyConflictException | met | Exception class defined |
| R-080b917def7f | concurrency | JobExecutionException | met | Exception class defined |
| R-31e87c3c4cac | concurrency | MaxRetriesExceededException | met | Exception class defined |
| R-5774aba39fa2 | Project-wide | Organizations are strictly isolated boundaries for data, users, projects, and settings. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-9b8dbc80eb57 | Project-wide | API authorization must enforce organization boundaries on every endpoint; knowing an object identifier from another organization must not grant access. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-58f19e2e682d | Project-wide | Requests targeting objects belonging to another organization must respond as unauthorized or unavailable to avoid revealing object existence. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-28cb7fe64bbb | Project-wide | Organization membership defines tenant access boundaries. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-024629bc90d0 | Project-wide | Search queries, administrative controls, and work item visibility must strictly enforce organization and project access constraints. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-b700ab784cfa | Project-wide | Background jobs must scope operations to their explicit target organization without leaking cross-tenant state. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-54e8ea840398 | Project-wide | Raw passwords and password-reset secrets must never be stored in plaintext. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-09a4307ba2aa | Project-wide | Password reset requests must not expose whether an email address belongs to an existing account. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-b9a26c7a746c | Project-wide | Changing an account password must invalidate all previously issued sessions. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-8fdaf0926342 | Project-wide | Server-side authorization checks must be enforced for all requests; client-side UI hiding is insufficient. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-fbd88e9b56f2 | Project-wide | All user-supplied content (comments, project descriptions, filenames) must be sanitized and escaped to prevent code execution and cross-site scripting (XSS). | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-94e62e97c881 | Project-wide | User-supplied filenames must not be used directly as filesystem paths to prevent path traversal vulnerabilities. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-3f9838c271b8 | Project-wide | The system must preserve historical activity records and contextual changes (e.g., status changes, assignee modifications, title updates). | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-64d5ff133b9e | Project-wide | Account deactivation, member removal, or comment/attachment deletion must not delete historical references or distort past audit trails. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-d0535b2928e6 | Project-wide | Destructive deletions (such as project deletion) must handle dependent objects (work items, comments, attachments, activities) to prevent orphaned records. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-0ebf9b5fee16 | Project-wide | Stored timestamps must remain unambiguous (UTC) across different geographical locations and viewer timezones. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-0999e14019ac | Project-wide | Organizations may specify a timezone setting for presenting dates and scheduled events. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-5c9c9145f4f6 | Project-wide | Work item due dates are calendar dates rather than time-specific instances and must remain consistent regardless of the viewer's timezone. | unclear | Work item management implementation is omitted. |
| R-3471a0741552 | Project-wide | Application architecture must not assume upload storage resides on the same server as the application. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-824922dad62d | Project-wide | File upload size limits must be enforced to prevent excessive storage consumption. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-7fb7266f93d8 | Project-wide | Authentication and authorization must be applied before generating or serving private file access or executing searches. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-3a2a17e8f4eb | Project-wide | Resource identifiers must be safe, and authorization must never rely on guessability. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-41be49b2bfa8 | Project-wide | File names supplied by users must not be trusted as filesystem paths or used for directory traversal. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-4502a1f9cb6c | Project-wide | Uploaded files are untrusted; their contents must not automatically be interpreted as HTML or executable code. | unclear | Unclear execution context provided |
| R-88036f7393c8 | Project-wide | Administrative pages and private data must reject unauthenticated or unauthorized access attempts regardless of URL knowledge. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-3f400c44decf | Project-wide | Validation errors, authorization failures, and server failures must be strictly distinguished. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-f1848979ee45 | Project-wide | Client retries and infrastructure failures must be handled cleanly via idempotency mechanisms and asynchronous processing without duplicating side effects. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-0e4e3dcba4b8 | Project-wide | Failures in peripheral services like email delivery or search indexing must not roll back core domain actions. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-f013529d3ff9 | Project-wide | Uploaded content must have reasonable limits and extremely large files must be rejected to prevent storage exhaustion. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-6574a228043c | Project-wide | Concurrent modifications to critical entities like ownership transfers and invitation acceptances must prevent duplicate records or conflicting states. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-6a03524259a6 | Project-wide | Timestamps must maintain unambiguous timezone interpretations. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-c8f88e008f89 | Project-wide | Organization timezones drive calendar displays without mutating underlying historical event timestamps. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-be0cba187f3b | Project-wide | Activity records and historical audit logs are append-only and must remain intelligible even if actors are removed or renamed. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |

## Remaining findings

### F-eff5108daed1: uncertain (medium)

File: src/organization_demo/work_item_management.py, line 355.
Requirements: R-135c25f0d74c

Comment content is stored raw without automatic sanitization.

Suggested correction: Sanitize comment content using render_comment_content upon addition.

Requirement evidence: Comment content must be treated as untrusted input and properly sanitized or escaped

Code evidence: comment = Comment(id=comment_id, author_id=auth_id, content=content, created_at=now)

Counterexample: Inputting '&lt;script&gt;alert(1)&lt;/script&gt;' stores unescaped markup.

### F-1a30ca011ae3: uncertain (medium)

File: src/organization_demo/administration.py, line 127.
Requirements: R-2f6f8527a206, R-100c7d3da11d

The idempotency_key parameter is accepted but not used to prevent duplicate logical records.

Suggested correction: Store and check idempotency keys to return existing invitation tokens on retry.

Requirement evidence: Retried operations must avoid creating duplicate logical records

Code evidence: def invite_member(self, requester_id: uuid.UUID, email: str, assigned_role: str = 'member', idempotency_key: Optional[str] = None) -&gt; str:

Counterexample: Calling invite_member with the same idempotency_key creates new invitation tokens.

### F-a64a2eb1e4e4: uncertain (low)

File: src/organization_demo/accounts_identity.py, line 159.
Requirements: R-5c9c9145f4f6

Work item due dates are not implemented in the provided modules.

Suggested correction: Implement work item due date handling if required.

Requirement evidence: Work item due dates are calendar dates rather than time-specific instances

Code evidence: due_date: Optional[datetime] = None

Counterexample: Viewing due dates across different timezones cannot be verified.

## Review limitations

- Static LLM review only; runtime behavior and tests have not been verified.
- Supplementary repository context is limited to 6 KB of tracked Python/configuration/documentation files.
- Review requests may further limit supplementary context to 2 KB and shorten interface outlines; full supplied source remains authoritative.
- Static analysis does not guarantee runtime behavior or correct thread synchronization.
- HTTP and UI layers are not present in this module.
- Static code review cannot verify all runtime behaviors.
- Static review does not prove runtime thread safety or asynchronous correctness.
- Static review does not prove runtime correctness.
- Static analysis does not execute runtime code or verify external storage persistence.
- Static review does not prove runtime thread safety under heavy load.
- Static review does not prove runtime correctness or database persistence guarantees.
- Project-wide checks omitted some full source files; unsupported absence claims remain unclear.
- Static review does not prove runtime correctness or thread scheduling behavior.
- Static review does not prove runtime cryptographic strength.
- Static code review does not prove full runtime correctness.
- Only selected source files were in scope for analysis.
- Static review does not prove runtime behavior.
- Work item management module was omitted from the source files.
- Static review does not prove runtime correctness or thread scheduling.
- Supplementary files omitted: src/organization_demo/comments_discussion.py, src/organization_demo/date_time_management.py, src/organization_demo/project_membership.py

This report was assembled from saved requirements, approved code, the repository baseline, and the current critic report. No additional model call was made.
