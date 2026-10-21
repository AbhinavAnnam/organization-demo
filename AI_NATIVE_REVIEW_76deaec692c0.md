# Northstar — change report

Run: `cfe32628-cb1d-4c0b-900f-c8bd78251308`
Candidate: `2922c341292e529d013d136a7b600a7bb92f78e270aa18444978690aa9a511f1`

## Change summary

198 requirements assessed; 4 confirmed defects, 1 uncertain findings, 0 suggestions.

Critic verdict: **changes_requested**. 198 requirements assessed.
Coverage: met: 163, partial: 4, missing: 0, unclear: 31.
Findings: 4 confirmed defects, 1 uncertain findings, 0 suggestions.

Repository: https://github.com/AbhinavAnnam/organization-demo.git
Base branch: `main`
Baseline commit: `9d72ea178fa43685d4c8ade57de888ae74d19c37`
Working branch: `ai-native/58302b77a0bb4300a4013d06d09e9d72`

## Files and modifications

| File | Change | Lines added | Lines removed |
| --- | --- | ---: | ---: |
| src/organization_demo/accounts_identity.py | added | 618 | 0 |
| src/organization_demo/comments_discussion.py | added | 321 | 0 |
| src/organization_demo/notifications_management.py | added | 354 | 0 |
| src/organization_demo/project_membership.py | added | 393 | 0 |
| src/organization_demo/search_service.py | added | 289 | 0 |

### src/organization_demo/accounts_identity.py

- Account: added
- AccountNotFoundException: added
- AccountsIdentityDirectory: added
- AuditLog: added
- AuthenticationError: added
- InvalidIdentifierException: added
- InvalidOrganizationSettingException: added
- InvalidOwnershipTransferException: added
- Invitation: added
- InvitationExpiredException: added
- MemberNotFoundException: added
- Membership: added
- Organization: added
- OrganizationAccessDeniedException: added
- OrganizationSettingValue: added
- OwnerRemovalException: added
- PrivilegeRevokedException: added
- ProjectMembership: added
- Session: added
- UnauthorizedAdminAccessException: added
- UnauthorizedOwnershipTransferException: added
- UnauthorizedRoleElevationException: added
- UnauthorizedSettingsUpdateException: added
- VerificationError: added

### src/organization_demo/comments_discussion.py

- Attachment: added
- AttachmentNotFoundException: added
- Comment: added
- CommentNotFoundException: added
- CommentService: added
- FileTooLargeException: added
- InvalidFilePathException: added
- ModerationPermissionException: added
- PathTraversalException: added
- UnauthorizedAttachmentAccessException: added
- UploadFailedException: added

### src/organization_demo/notifications_management.py

- EmailDeliveryException: added
- EmailTemplate: added
- InvalidEmailTokenException: added
- InvalidNotificationPreferenceException: added
- Notification: added
- NotificationDeliveryException: added
- NotificationEventType: added
- NotificationService: added
- _default_email_sender: added

### src/organization_demo/project_membership.py

- AccessRevokedException: added
- ConcurrentModificationException: added
- InvalidStateTransitionException: added
- MalformedWorkItemException: added
- Organization: added
- OrganizationDirectory: added
- OrphanedDataException: added
- Project: added
- ProjectMember: added
- ProjectMembershipManager: added
- ProjectNotFoundException: added
- ProjectOwnerRequiredException: added
- UnauthorizedObjectAccessException: added
- ValidationError: added
- WorkItem: added

### src/organization_demo/search_service.py

- ActivityEntry: added
- ActivityLogImmutableException: added
- DashboardSummary: added
- SearchIndexingException: added
- SearchResult: added
- SearchService: added
- UnauthorizedSearchAccessException: added

## Validation and testing

- Approved Python files were checked for valid syntax and matched to the reviewed candidate.
- **Automated tests were not run in this delivery workflow. The testing phase was skipped.**
- The critic is a static, model-assisted assessment; its verdict does not establish runtime correctness.
- Remaining findings are disclosed below for the pull request reviewer.

## Requirement coverage

| Requirement | Module | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| R-119a88e41485 | accounts_identity | Northstar accounts are based around an email address, but the email address is not considered an organization's identity for authorization purposes. | unclear | Authorization context implies multi-org rules but email is not directly used for auth checks. |
| R-51061dc63523 | accounts_identity | A person joining two organizations should continue using the same account rather than creating a second account for each organization. | met | Accounts are keyed by account_id and email mapping. |
| R-3ca3ab6f2e59 | accounts_identity | A new user provides an email address and password and is subsequently asked to verify ownership of that address. | met | register_account creates a verification token. |
| R-b20d62f742ee | accounts_identity | Until verification is completed, the account may exist but should not be treated as fully active. | unclear | is_verified exists but authentication does not block unverified accounts. |
| R-fe92342c8707 | accounts_identity | External identity providers are not required for the initial release, but the account model should not assume an account must always authenticate using a password. | met | Account model does not restrict authentication mechanisms. |
| R-96b581ae22ff | accounts_identity | Email addresses are treated case-insensitively for account lookup, preventing separate accounts from being created due to capitalization differences. | met | normalized_email = email.strip().lower() |
| R-65a7a42feb86 | accounts_identity | A password reset begins from the sign-in experience and can be requested without an authenticated session. | met | request_password_reset takes email without auth session. |
| R-d62d5f842612 | accounts_identity | The password reset mechanism must not reveal whether a particular email address belongs to an existing account. | met | request_password_reset returns None for missing emails silently. |
| R-4f14bc0672b2 | accounts_identity | Password-reset links are temporary, and once a reset is successfully completed, an old reset link should not remain usable. | met | reset_password invalidates sessions and clears token. |
| R-514b55d7c173 | accounts_identity | Sessions should be invalidated when appropriate security-sensitive actions occur, such as changing a password, so that previously issued sessions are not permanently trusted. | met | change_password invalidates all sessions for the account. |
| R-56816a568b87 | accounts_identity | The system should avoid storing raw passwords or password-reset secrets. | met | _hash_password uses sha256. |
| R-c3e4d1b61078 | accounts_identity | Users can change their own profile information, including a display name that is not forced to equal the email address. | met | update_profile allows display name updates. |
| R-cc8eb7359e0c | accounts_identity | A user may deactivate their account, but organizations must not unexpectedly lose historical references merely because the individual is no longer active. | met | deactivate_account sets is_active to False without deleting records. |
| R-05dfa937d607 | accounts_identity | The first user creating an organization becomes its initial owner. | met | create_organization assigns creator as owner. |
| R-44d9af19fc13 | accounts_identity | An organization has a name and may optionally have a short identifier used in URLs and integrations, which must be unique enough to avoid ambiguous routing. | met | slug uniqueness checking is implemented. |
| R-a7a9cc692818 | accounts_identity | Organizations are isolated from one another; a member of Organization A should not gain access to Organization B via shared email addresses or known object identifiers. | met | _get_membership scopes actions by organization_id. |
| R-d3e07f3aee67 | accounts_identity | API authorization must strictly enforce organization boundaries. | met | invite_member checks actor membership and role. |
| R-fb85345a2647 | accounts_identity | An organization owner can invite additional people by email address. | met | invite_member allows inviting by email. |
| R-0abc40822171 | accounts_identity | Accepting an invitation adds an existing account to the organization or becomes part of the registration process for new users without creating duplicate identities. | met | accept_invitation adds membership or reactivates. |
| R-679af3ccce53 | accounts_identity | Invitations should not remain valid indefinitely and can be revoked by an administrator to prevent subsequent acceptance. | met | revoke_invitation sets is_revoked to True. |
| R-cce7f1c5d9b5 | accounts_identity | Accepting an invitation from one organization must not consume or invalidate unrelated invitations from other organizations. | met | accept_invitation targets specific invitation IDs. |
| R-6146a2b03724 | accounts_identity | Organizations may have their own timezone setting affecting how dates and scheduled events are presented, while stored timestamps remain unambiguous. | met | Organization dataclass stores timezone. |
| R-2ff1cbf614b3 | accounts_identity | Organization names may be changed later, and references in historical activity should remain understandable. | met | update_organization_settings allows updating name. |
| R-a80a4f43f761 | accounts_identity | Organization administrators can configure workspace settings including organization name and organization timezone. | met | update_organization_settings handles name and timezone. |
| R-a2affb083743 | accounts_identity | Settings are strictly scoped to the organization rather than global user preferences. | met | Organization settings are stored within the organization mapping. |
| R-381f12f9976e | accounts_identity | Changing an organization timezone affects future date display interpretations but must not rewrite existing activity timestamps. | met | Timezone updates do not alter audit log timestamps. |
| R-0c01da70016e | accounts_identity | Settings updates are recorded in administrative activity history. | met | update_organization_settings appends audit log entries. |
| R-813560ee46e8 | accounts_identity | Organizations retain sensible defaults when settings have not been explicitly configured. | met | Organization timezone defaults to UTC. |
| R-27bcd9e3055e | accounts_identity | The system must distinguish between an absent optional setting and a explicitly selected default setting. | met | OrganizationSettingValue uses explicitly_set flag. |
| R-bd156dec5f16 | accounts_identity | The administration area provides controls for membership management, pending invitations, organization settings, and security info. | unclear | Admin controls span multiple methods without a single unified UI route. |
| R-870f7fdfd0f0 | accounts_identity | Administrators can inspect current members and assigned roles. | met | inspect_members lists members and roles. |
| R-dc85c71ac818 | accounts_identity | Administrative routes must strictly enforce authorization and cannot be bypassed by direct URL navigation. | met | Administrative methods explicitly check session validity and role. |
| R-cf1a9535b1ed | accounts_identity | If administrative privileges are revoked during an active session, administrative operations must be blocked immediately on subsequent requests. | met | update_organization_settings raises PrivilegeRevokedException if membership is inactive. |
| R-e53714c3a9a6 | accounts_identity | Destructive and sensitive operations (removing members, deleting projects, transferring ownership) require explicit confirmation. | unclear | Destructive operations are supported via specific methods, but confirmation logic is absent. |
| R-b988afe6d62e | accounts_identity | The user interface must clearly distinguish 'remove from project' from 'remove from organization'. | met | remove_member and remove_from_project are separate methods. |
| R-fab68f170a94 | accounts_identity | The initial product has three broad levels of access: owner, administrator, and member. | met | Membership roles support owner, administrator, and member. |
| R-7cd100695ca8 | accounts_identity | The owner is responsible for organization-level control with normally one owner at a time, though ownership can be transferred. | met | transfer_ownership supports ownership management. |
| R-2d5d8c10d8be | accounts_identity | Administrators can manage operational aspects but cannot perform actions reserved exclusively for the owner. | met | invite_member restricts non-owners from performing owner actions. |
| R-301b3a3bd804 | accounts_identity | Ordinary members can participate in projects and work but are not presented with organization-wide controls. | met | Ordinary members lack administrative checks. |
| R-0e111f9959fa | accounts_identity | Server-side authorization checks are mandatory and members cannot elevate their own permissions by modifying server requests. | met | Server-side role checks are enforced in methods. |
| R-1b3a83992a79 | accounts_identity | Removing a member from an organization immediately prevents access to organization data through normal authenticated requests, but does not rewrite historical activity or make assignments disappear. | met | remove_member sets is_active to False immediately. |
| R-8b9a29c343bb | accounts_identity | The current organization owner can transfer ownership to another active member of the same organization. | met | transfer_ownership allows transferring to an active member. |
| R-1e2cad00e9b2 | accounts_identity | The recipient of ownership must already be an existing member of the organization. | met | transfer_ownership checks recipient_membership is active. |
| R-91344887d9e2 | accounts_identity | Ownership transfer reassigns organizational responsibility without creating duplicate organization instances. | met | transfer_ownership reassigns roles. |
| R-a3053ef2944b | accounts_identity | The previous owner is assigned an administrator or member role based on selection during the transfer operation. | met | transfer_ownership accepts previous_owner_new_role. |
| R-fa9546ffd5ad | accounts_identity | Ownership transfer events must be permanently recorded in administrative logs. | met | transfer_ownership appends audit log entry. |
| R-9755fb9a0652 | accounts_identity | Recovery of ownership for deactivated or removed accounts requires elevated operational procedures. | unclear | Elevated recovery procedures for removed accounts are not explicitly implemented. |
| R-28da13428ca6 | accounts_identity | AuthenticationError | met | AuthenticationError exception is defined. |
| R-ec1884be3b9a | accounts_identity | VerificationError | met | VerificationError exception is defined. |
| R-8a1202ae09a6 | accounts_identity | AccountNotFoundException | met | AccountNotFoundException exception is defined. |
| R-401165a1b379 | accounts_identity | OrganizationAccessDeniedException | met | OrganizationAccessDeniedException exception is defined. |
| R-93f1bfc803fc | accounts_identity | InvitationExpiredException | met | InvitationExpiredException exception is defined. |
| R-c4222adfda4c | accounts_identity | InvalidIdentifierException | met | InvalidIdentifierException exception is defined. |
| R-4a89af572487 | accounts_identity | InvalidOrganizationSettingException | met | InvalidOrganizationSettingException exception is defined. |
| R-ad2c351b4701 | accounts_identity | UnauthorizedSettingsUpdateException | met | UnauthorizedSettingsUpdateException exception is defined. |
| R-723964163386 | accounts_identity | UnauthorizedAdminAccessException | met | UnauthorizedAdminAccessException exception is defined. |
| R-fbba5519b04c | accounts_identity | PrivilegeRevokedException | met | PrivilegeRevokedException exception is defined. |
| R-a4cf6c77cf67 | accounts_identity | UnauthorizedRoleElevationException | met | UnauthorizedRoleElevationException exception is defined. |
| R-95b0416df75b | accounts_identity | OwnerRemovalException | met | OwnerRemovalException exception is defined. |
| R-767e95fb448a | accounts_identity | InvalidOwnershipTransferException | met | InvalidOwnershipTransferException exception is defined. |
| R-1912e13c05d7 | accounts_identity | MemberNotFoundException | met | MemberNotFoundException exception is defined. |
| R-4dba57b1312f | accounts_identity | UnauthorizedOwnershipTransferException | met | UnauthorizedOwnershipTransferException exception is defined. |
| R-478d3f3e5163 | project_membership | A project represents a body of related work and has a name, description, creator, owner, status, timestamps, and membership information. | met | Project dataclass has name, description, creator, owner, status, timestamps, and members. |
| R-c58f10ac861a | project_membership | Project access is considered separately from organization membership, and persons outside the organization cannot be added directly to a project. | met | add_project_member checks org_members to prevent adding non-organization members. |
| R-55e4b03100a9 | project_membership | Completing or archiving a project is preferable to permanently deleting it, and archived projects do not appear in primary selection views but remain inspectable by authorized users. | met | archive_project sets status to archived, keeping it inspectable. |
| R-f679427d5640 | project_membership | Project names do not need to be globally unique. | met | create_project does not enforce uniqueness checks on names. |
| R-05cce8f035c7 | project_membership | Deleting a project is a destructive operation that must consider dependent work items, comments, attachments, and activity records. | met | delete_project permanently removes the project. |
| R-268c6d6f4b4d | project_membership | Project descriptions may contain ordinary formatting but must not be interpreted as executable content. | met | _sanitize_description escapes description text. |
| R-e94d12752f09 | project_membership | A project can have an optional due date. | met | Project has optional due_date field. |
| R-001850dea3a4 | project_membership | A project owner can add and remove members, and organization administrators may need equivalent capabilities. | met | add_project_member and remove_project_member manage members. |
| R-cbda25181c2c | project_membership | A removed project member loses access to project-specific information restricted to participants. | met | remove_project_member deletes the member from project members. |
| R-46c67640b358 | project_membership | Existing work assigned to a removed member is not automatically deleted or reassigned. | met | Work items are not reassigned upon member removal. |
| R-f4a5a2fbade2 | project_membership | A project owner cannot be removable through an ordinary member-removal action without another owner being designated to avoid leaving an active project without an owner. | met | remove_project_member checks owner count before removing an owner. |
| R-a36c9b75c419 | project_membership | A work item belongs to one project and at minimum has a title and a status. | met | WorkItem dataclass has title and status. |
| R-3ef73b83a028 | project_membership | The initial workflow consists of three states: not yet completed, currently being worked on, and completed. | met | WorkItem defaults status to not_yet_completed and supports in_progress and completed. |
| R-26cba0cd5581 | project_membership | An item marked complete can subsequently return to an active state. | met | update_work_item allows changing status back to active. |
| R-c96c24dc781c | project_membership | Priority is represented using a small ordered range rather than arbitrary numeric values. | met | Priority uses a string range. |
| R-afc18cd8b7ac | project_membership | A work item may have no assignee, and unassigned work is legitimate during planning. | met | assignee_id defaults to None. |
| R-83b7dca84ead | project_membership | Due dates are dates rather than precise moments, remaining due on that calendar date regardless of the viewer's timezone. | met | due_date uses date type. |
| R-88c8de0f5b5c | project_membership | Work items can be reordered within project views to reflect user preference. | met | update_work_item allows changing position. |
| R-d9c37927e315 | project_membership | Most fields can be changed after creation, governed by project permissions. | met | update_work_item updates fields. |
| R-fdc4658b58b3 | project_membership | Changes to titles, statuses, and assignees are recorded in historical activity. | met | update_work_item records title, status, and assignee changes in history. |
| R-eb9fedd87ab1 | project_membership | A user should be able to remove an optional due date after it has been set. | met | update_work_item accepts clear_due_date to remove due date. |
| R-79503b91cde9 | project_membership | The API must reject malformed identifiers and invalid state values rather than silently converting them. | met | create_project and update_work_item raise ValidationError for malformed inputs. |
| R-2753af12c6e9 | project_membership | Requests involving an object belonging to another organization must behave as unauthorized or unavailable. | met | get_project raises UnauthorizedObjectAccessException for mismatched organization name. |
| R-29e636f5d386 | project_membership | ProjectNotFoundException | met | ProjectNotFoundException is defined. |
| R-8af9594e9d26 | project_membership | OrphanedDataException | met | OrphanedDataException is defined. |
| R-a44e5b6abcca | project_membership | ProjectOwnerRequiredException | met | ProjectOwnerRequiredException is defined. |
| R-250406951a22 | project_membership | AccessRevokedException | met | AccessRevokedException is defined. |
| R-1ae81f66e39b | project_membership | InvalidStateTransitionException | met | InvalidStateTransitionException is defined. |
| R-7b245f9d5130 | project_membership | MalformedWorkItemException | met | MalformedWorkItemException is defined. |
| R-4e92cb6cbef6 | project_membership | ValidationError | met | ValidationError is defined. |
| R-fd86e1b3adfc | project_membership | UnauthorizedObjectAccessException | met | UnauthorizedObjectAccessException is defined. |
| R-215da4c46190 | comments_discussion | Comments belong directly to the work item as threaded discussion is not included in the first release. | met | Implemented in CommentService |
| R-b52d175d8cda | comments_discussion | Users can edit their own comments, and organization administrators may moderate comments in exceptional circumstances. | met | Implemented in edit_comment |
| R-17d2d7f01e0d | comments_discussion | Deleting a comment indicates that content was removed in the activity history without completely hiding that the comment existed. | met | Implemented in delete_comment |
| R-71ce448310b4 | comments_discussion | Stored comment representations must be treated as untrusted input and safely rendered to prevent XSS attacks. | met | Implemented in render_comment_content |
| R-f820b133ed3b | comments_discussion | Attachments may be uploaded directly to a work item and associated with an individual comment. | met | Implemented in add_attachment |
| R-bbbe8e532dc6 | comments_discussion | File storage is an implementation concern and content does not need to reside on the application server. | met | Implemented via storage_id |
| R-74d7375284a1 | comments_discussion | Reasonable limits must exist around uploaded content, and extremely large files should be rejected. | met | Implemented in add_attachment |
| R-1306ccc7a07f | comments_discussion | File names supplied by users must not be trusted as filesystem paths. | met | Implemented in _contains_path_traversal |
| R-293305ad1ea7 | comments_discussion | Deleting an attachment removes it from normal access while historical activity indicates the removal. | met | Implemented in delete_attachment |
| R-3f4c6890cf6d | comments_discussion | Attachments can be uploaded directly to a work item or associated with an individual comment. | met | Implemented in add_attachment |
| R-896fa890e6a4 | comments_discussion | The application must not assume uploaded content resides on the same server as the application itself. | met | Implemented via storage_id |
| R-2b6ebfd7ae56 | comments_discussion | File size limits must be enforced, and extremely large files must be rejected rather than consuming unlimited storage. | met | Implemented in add_attachment |
| R-b0eb4df27120 | comments_discussion | User-supplied file names must not be trusted as filesystem paths. | met | Implemented in _contains_path_traversal |
| R-ac6a894f6aa2 | comments_discussion | Multiple files may share the same display name without representing the same attachment. | met | Attachments use unique UUIDs |
| R-3e29cfba7047 | comments_discussion | Deleting an attachment removes it from normal access, but historical activity may indicate removal without retaining a publicly accessible file copy. | met | Implemented in delete_attachment |
| R-264ffd5d0ee5 | comments_discussion | An attachment inherits the access rules of its parent work item. | unclear | Work item access rules not in scope |
| R-f5a9e4620b47 | comments_discussion | Knowledge of a storage identifier is insufficient to retrieve a private file. | met | Implemented in get_attachment |
| R-21db123c5307 | comments_discussion | Downloads must be authorized independently from the page displaying the work item. | unclear | Independent download endpoint not supplied |
| R-bf098eb2e2e3 | comments_discussion | Unsupported file formats must be offered as downloadable content when inline preview is unavailable. | unclear | Inline preview not supplied |
| R-97df0edf126b | comments_discussion | ModerationPermissionException | met | ModerationPermissionException defined |
| R-14c246c08782 | comments_discussion | CommentNotFoundException | met | CommentNotFoundException defined |
| R-4f258edc1acb | comments_discussion | FileTooLargeException | met | FileTooLargeException defined |
| R-7dfdc4639f27 | comments_discussion | PathTraversalException | met | PathTraversalException defined |
| R-b71792847600 | comments_discussion | UploadFailedException | met | UploadFailedException defined |
| R-146b6e01df28 | comments_discussion | InvalidFilePathException | met | InvalidFilePathException defined |
| R-7c61ae49f4bb | comments_discussion | UnauthorizedAttachmentAccessException | met | UnauthorizedAttachmentAccessException defined |
| R-4929445b8619 | comments_discussion | AttachmentNotFoundException | met | AttachmentNotFoundException defined |
| R-2b67e81806c3 | notifications_management | Users are notified of relevant work events, such as being assigned a work item or mentioned in a comment. | unclear | No trigger logic implemented for work item assignment or comment mentions. |
| R-21df0056e050 | notifications_management | Comments on followed items generate notifications based on user notification settings. | met | COMMENT_ON_FOLLOWED_ITEM checks notification settings. |
| R-16c44bb301c6 | notifications_management | Internal bookkeeping database changes without user-facing significance must remain invisible and not trigger notifications. | unclear | No logic filters out internal bookkeeping database changes. |
| R-fd8eced8bf34 | notifications_management | Notifications must identify the event sufficiently for the user to understand its origin. | met | Notification includes message and event_type. |
| R-1c2e825a4a00 | notifications_management | Notifications can be marked as read without deleting them. | met | mark_as_read updates read_at without deleting. |
| R-734fdbb9c103 | notifications_management | The notification list must distinguish unread items from previously viewed items. | met | list_notifications sorts unread items first. |
| R-e0a8d2dcf7e9 | notifications_management | Disabling email notifications does not disable the underlying event or remove in-app notifications unless explicitly configured as the same preference. | unclear | No distinct configuration logic separating email from in-app notifications. |
| R-0b9d414bdb33 | notifications_management | Failed email delivery must not roll back the underlying assignment or comment mention. | met | Email failures handled asynchronously without rolling back actions. |
| R-764a46bcb660 | notifications_management | The system must prevent generating duplicate notifications when an operation is retried. | met | Deduplication via _generated_keys prevents duplicate notifications. |
| R-c4a885351f06 | notifications_management | Transactional email is used for account verification, password recovery, invitations, and selected notifications. | unclear | No implementation for transactional email triggers on verification or password recovery. |
| R-f788a8a230e7 | notifications_management | Emails containing authentication or invitation links must use temporary credentials or tokens and never expose passwords. | unclear | No enforcement of temporary credentials or tokens for auth/invitation links. |
| R-760c1e5a4c1a | notifications_management | Email templates can be updated independently of main application logic. | unclear | Templates are hardcoded data classes without independent storage/update mechanisms. |
| R-baeca53d4f3c | notifications_management | Email sending must occur asynchronously where practical to prevent blocking user action confirmation. | met | Emails dispatched asynchronously via background threads. |
| R-c23629a9191f | notifications_management | Email delivery failures must be handled gracefully without rolling back primary actions. | met | Email delivery exceptions caught and logged without rollback. |
| R-e79e92a70b5d | notifications_management | Email addresses must not be logged unnecessarily in broadly accessible operational logs. | unclear | No logic preventing email addresses from being written to operational logs. |
| R-5953c6fdc2da | notifications_management | The system must distinguish between successful invitation creation and the attempt to deliver the email. | met | send_invitation returns boolean on hand-off success. |
| R-0b3f39475418 | notifications_management | NotificationDeliveryException | partial | Exception defined but not raised by NotificationService. |
| R-b6ba6a88a77d | notifications_management | InvalidNotificationPreferenceException | met | Raised in set_email_notifications_enabled. |
| R-596d07f4c2be | notifications_management | EmailDeliveryException | unclear | Exception defined and caught internally, but not exposed publicly. |
| R-1946408f85c9 | notifications_management | InvalidEmailTokenException | met | Raised in validate_email_token. |
| R-40626488a9e7 | search_service | Search spans accessible operational content including project names, project descriptions, work item titles, work item descriptions, and comments. | met | Search spans titles, contents, and snippets across accessible items. |
| R-cae32b0d6759 | search_service | Search must enforce organization and project access boundaries; users must not discover projects or items they cannot open. | met | Enforces organization, project access, and allowed user IDs. |
| R-156405590585 | search_service | Search results must provide surrounding context to explain why a result matched. | met | Snippet context is built around matches. |
| R-53322c9ef5b6 | search_service | Search performs partial matching over exact title matching. | met | Performs substring search over lowercase text. |
| R-003cabdff496 | search_service | Search indexing occurs asynchronously; new items may take a short duration to appear in search results. | met | Indexing is synchronous/asynchronous via index_document. |
| R-b37ac4e13aec | search_service | Deleting or restricting access to an object must eventually remove it from search results for unauthorized users. | met | Documents can be removed or deactivated. |
| R-11da06b68a6c | search_service | Search ranking is non-contractual and clients must not rely on a fixed ranking algorithm. | met | No ranking algorithm is implemented. |
| R-e45eb409442e | search_service | The dashboard summarizes active projects and work assigned to the current user. | met | Dashboard summarizes active projects and assigned work. |
| R-41190b30d05d | search_service | Completed and archived work must not dominate the default dashboard view. | met | Filters out completed and archived work from defaults. |
| R-4d39712caed8 | search_service | A user with no assigned work must see a helpful empty state rather than a technical error. | met | Sets helpful empty_state_message when no work. |
| R-1052411f0c28 | search_service | Recently updated items reflect meaningful user-facing changes rather than arbitrary database timestamp modifications. | met | Sorts recently updated items by last_meaningful_update. |
| R-b1652bfd5842 | search_service | Date-oriented information on the dashboard is presented according to the organization's configured timezone. | met | Localizes dates using timezone_str and ZoneInfo. |
| R-93eb0bd2097e | search_service | Dashboard metrics and counts must be derived from current accessible data dynamically. | met | Metrics derived dynamically from passed lists. |
| R-616f57fc3bbc | search_service | Significant activities recorded include project creation, ownership changes, member additions/removals, work item creation, assignment changes, status changes, and administrative actions. | met | record_activity accepts various actions and targets. |
| R-6c8d52140c40 | search_service | Activities include the actor identifier where an identifiable actor exists; system-generated activities may lack a human actor. | met | Stores actor_id and actor_name optionally. |
| R-3aca4a00901b | search_service | Activities store consistent, unambiguous timestamps. | met | Timestamps use UTC datetime. |
| R-1e00bf851cff | search_service | Internal database operations (index updates, cache refreshes, email retries) must not appear in the user activity feed. | met | Excludes INTERNAL_ prefixed actions from lists. |
| R-96e778e56a3b | search_service | Activity entries remain intelligible if an actor's display name changes, or if the user is deactivated or removed, without granting deactivated identities new access. | met | Stores actor references independently of live changes. |
| R-3ca89abc8c98 | search_service | Activity records are append-only; ordinary users cannot modify historical records. | unclear | No explicit enforcement preventing external list mutation. |
| R-8d706dbb1d7c | search_service | Administrators may be granted broader access to activity audit logs than regular project members. | partial | is_admin parameter is accepted but not enforced. |
| R-a9c5fcdf8c5c | search_service | SearchIndexingException | met | SearchIndexingException is defined. |
| R-b81edcdea756 | search_service | UnauthorizedSearchAccessException | met | UnauthorizedSearchAccessException is defined. |
| R-fc2d206d8d35 | search_service | ActivityLogImmutableException | met | ActivityLogImmutableException is defined. |
| R-6c8799b56cad | Project-wide | Email addresses are treated case-insensitively. | met | normalized_email = email.strip().lower() |
| R-83092ef88180 | Project-wide | Password reset mechanisms must not disclose account existence. | met | return None |
| R-aed84b656750 | Project-wide | Sessions must be invalidated upon security-sensitive actions like password changes. | met | session.is_valid = False |
| R-b6267fe22f3a | Project-wide | Storage of raw passwords or password-reset secrets is strictly prohibited. | met | return hashlib.sha256(password.encode("utf-8")).hexdigest() |
| R-619860019943 | Project-wide | Organization isolation must be enforced consistently across both the web interface and API authorization layers. | unclear | No web interface supplied |
| R-54fa78746a14 | Project-wide | User-supplied input in project descriptions, comments, and file names must be sanitized, escaped, or treated as untrusted to prevent security vulnerabilities such as XSS and path traversal. | met | self._sanitize_description(description) |
| R-5f830383b0d2 | Project-wide | Historical activity and audit trails must be preserved when users are deactivated, removed from organizations or projects, or when comments and attachments are deleted. | met | Mark a comment as deleted; content remains in history. |
| R-589312a4ecda | Project-wide | Deactivation or removal actions must not corrupt or silently erase historical data associations. | met | target_membership.is_active = False |
| R-2c62055a3125 | Project-wide | Organizations may configure custom timezones that affect presentation, while stored timestamps remain globally unambiguous. | met | timezone: str = "UTC" |
| R-177469d6f49a | Project-wide | Due dates for ordinary work items and projects are evaluated as calendar dates independent of viewer timezones. | met | due_date: Optional[date] = None |
| R-b609250f3c00 | Project-wide | Visibility follows a layered model: organization membership determines tenant access, project access restricts project scopes, and work items/comments/attachments inherit project visibility. | unclear | Full layered permission check implementation not supplied |
| R-a72cf8039a4d | Project-wide | API endpoints returning child objects (comments, attachments) must explicitly verify permissions against the parent work item and project. | unclear | API layer omitted from supplied files |
| R-e3556b431011 | Project-wide | Downloading attachments must enforce project membership authorization checks rather than relying on unguessable file identifiers. | partial | if not is_admin:<br>    raise UnauthorizedAttachmentAccessException |
| R-e66ddc40aa56 | Project-wide | Unauthenticated access to private resources via public sharing links is explicitly prohibited in the initial release. | unclear | Public sharing links implementation omitted |
| R-ea2cc36abbb5 | Project-wide | Resource identifiers in APIs must be safe to expose; authorization must never rely on unguessable sequential numeric IDs alone. | met | account_id = secrets.token_hex(8) |
| R-b8b34eae4d86 | Project-wide | Validation errors must be clearly distinguishable from authorization failures and server failures. | met | raise AuthenticationError |
| R-1c179e909ebf | Project-wide | Malformed API requests must not expose internal stack traces or implementation details in normal responses. | unclear | API error handling middleware not provided |
| R-0f6a9e3ce041 | Project-wide | Modifying operations must return sufficient resource details for clients to update local UI without forcing full page reloads. | unclear | API response payloads unsupplied |
| R-5e154d970793 | Project-wide | Paginated endpoints are mandatory for unbounded collections (members, projects, notifications, search, activity feeds) with stable ordering across pages. | partial | inspect_members(..., limit: int = 50, offset: int = 0) |
| R-6c32da8e120f | Project-wide | Simultaneous updates to distinct attributes of a work item by multiple users must be supported without corrupting unrelated data. | met | if changes:<br>    work_item.version += 1 |
| R-35453fc0fae6 | Project-wide | Stale client views must not overwrite newer changes for critical fields and state updates. | met | if expected_version is not None and work_item.version != expected_version:<br>    raise ConcurrentModificationException |
| R-e68efba5acb6 | Project-wide | Strict concurrency control and idempotency must prevent duplicate side effects on operations such as membership modifications, ownership transfers, and invitation acceptances. | met | invitation.is_revoked = True  # Consume invitation |
| R-f284316c84aa | Project-wide | Core business operations must be isolated from external dependency failures (e.g., search indexing or email failures must not roll back work item creation or assignment). | unclear | External service integration not present |
| R-3eb1ea1d9bc3 | Project-wide | Retries triggered by network timeouts or background workers must be idempotent and avoid creating duplicate logical records or duplicate user-visible side effects. | unclear | Network retry mechanisms omitted |
| R-27dd4128e009 | Project-wide | Asynchronous background processing must be used for email delivery, search indexing, notification generation, and file processing. | met | thread = threading.Thread(target=worker, daemon=True) |
| R-a2ac6b594120 | Project-wide | Background jobs must capture explicit organization and resource context without relying on transient web session state. | unclear | Background job queue runner context unsupplied |
| R-a27a017ce217 | Project-wide | Failed background jobs must support retry limits and operational visibility for monitoring and investigation. | unclear | Background job retry execution code omitted |
| R-1b8c39ed02a3 | Project-wide | User-supplied filenames are untrusted and must be sanitized to prevent directory traversal attacks (e.g., ../../something). | met | if self._contains_path_traversal(display_name):<br>    raise PathTraversalException |
| R-85a7a5cc0b20 | Project-wide | File contents must not be automatically executed or rendered as HTML; proper Content-Disposition headers must be applied on download. | unclear | HTTP download response generation omitted |
| R-00b8098a4d5f | Project-wide | Private file download URLs generated with temporary access must have strict time limits and enforce authentication prior to access. | unclear | Temporary access URL generation unsupplied |
| R-5d129358078e | Project-wide | File upload limits must be validated before allowing unbounded data streaming. | met | if size_bytes &gt; self.MAX_FILE_SIZE_BYTES:<br>    raise FileTooLargeException |
| R-954cacb3957f | Project-wide | Event timestamps must be stored with unambiguous UTC/timezone representations. | met | created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc)) |
| R-ee9421d4a290 | Project-wide | Work item due dates represent whole calendar days rather than exact time instants and must not shift unexpectedly across timezone changes. | met | due_date: Optional[date] = None |
| R-239be30c6d69 | Project-wide | Relative time labels ('today', 'tomorrow') must be computed dynamically using the current user or organization context. | unclear | Dynamic relative time label formatting unsupplied |
| R-666ff2e8a4d1 | Project-wide | Daylight-saving time transitions must be accounted for without assuming every day has 24 hours in calendar logic. | unclear | DST calendar transition logic unsupplied |

## Remaining findings

### F-72d9b9770a58: uncertain (medium)

File: src/organization_demo/accounts_identity.py, line 161.
Requirements: R-b20d62f742ee

Authentication permits unverified accounts to sign in.

Suggested correction: Add check for account.is_verified in authenticate method.

Requirement evidence: Until verification is completed, the account may exist but should not be treated as fully active.

Code evidence: def authenticate(self, email: str, password: str) -&gt; Session:

Counterexample: Unverified user successfully authenticates.

### F-18dc316111e4: defect (medium)

File: src/organization_demo/notifications_management.py, line 23.
Requirements: R-0b3f39475418

NotificationDeliveryException is defined but never raised within notification service operations.

Suggested correction: Raise NotificationDeliveryException when delivery fails or remove it if unused.

Requirement evidence: NotificationDeliveryException

Code evidence: class NotificationDeliveryException(Exception):

Counterexample: Failing to deliver a notification does not raise NotificationDeliveryException.

### F-f71809046974: defect (medium)

File: src/organization_demo/search_service.py, line 160.
Requirements: R-8d706dbb1d7c

Admin access parameter is not checked during log listing.

Suggested correction: Enforce administrator permissions using the is_admin parameter.

Requirement evidence: Administrators may be granted broader access

Code evidence: def list_activities(

Counterexample: Regular users calling list_activities with is_admin=False receive unrestricted logs.

### F-2d2bc3ac9f01: defect (medium)

File: src/organization_demo/comments_discussion.py, line 269.
Requirements: R-e3556b431011

Attachment access relies on an admin flag rather than verifying project membership.

Suggested correction: Implement project membership validation checks in get_attachment.

Requirement evidence: Downloading attachments must enforce project membership authorization checks

Code evidence: if not is_admin:<br>    raise UnauthorizedAttachmentAccessException

Counterexample: A valid project member without admin rights gets UnauthorizedAttachmentAccessException.

### F-6eedde54aefb: defect (low)

File: src/organization_demo/accounts_identity.py, line 352.
Requirements: R-5e154d970793

Pagination is implemented for members, but notifications, search, and activity feeds lack offset/limit pagination.

Suggested correction: Add limit and offset parameters to notifications, search, and activity listing methods.

Requirement evidence: Paginated endpoints are mandatory for unbounded collections

Code evidence: def inspect_members(self, session_id: str, organization_id: str, limit: int = 50, offset: int = 0) -&gt; List[Membership]:

Counterexample: search() returns all matching items without pagination parameters.

## Review limitations

- Static LLM review only; runtime behavior and tests have not been verified.
- Supplementary repository context is limited to 6 KB of tracked Python/configuration/documentation files.
- Review requests may further limit supplementary context to 2 KB and shorten interface outlines; full supplied source remains authoritative.
- Static review does not execute runtime code paths.
- Static code review cannot verify runtime behavior or external database state.
- Static code analysis cannot verify runtime behavior or external storage security properties.
- Static review cannot confirm asynchronous thread safety or actual network email delivery behavior.
- Static review does not prove runtime correctness.
- Static review cannot verify runtime database behavior or HTTP transport layers.
- Several modules omit API request/response wrappers and frontend components.

This report was assembled from saved requirements, approved code, the repository baseline, and the current critic report. No additional model call was made.
