# Northstar — change report

Run: `6b5a7b12-9498-4de1-8bfc-e84fba673875`
Candidate: `f087e5e52ff00ff046d048e433d632c7dcc81dad146a0fbfc77f0d10162b3fb9`

## Change summary

198 requirements assessed; 7 confirmed defects, 1 uncertain findings, 0 suggestions.

Critic verdict: **changes_requested**. 198 requirements assessed.
Coverage: met: 152, partial: 7, missing: 0, unclear: 39.
Findings: 7 confirmed defects, 1 uncertain findings, 0 suggestions.

Repository: https://github.com/AbhinavAnnam/organization-demo.git
Base branch: `main`
Baseline commit: `74a27995c586e8336d7a8019e2809f18a6f9e618`
Working branch: `ai-native/45a0f536bfd64148a9d3aa4725281ba0`

## Files and modifications

| File | Change | Lines added | Lines removed |
| --- | --- | ---: | ---: |
| src/organization_demo/accounts_identity.py | modified | 1 | 1 |
| src/organization_demo/comments_discussion.py | modified | 141 | 110 |
| src/organization_demo/notifications_management.py | modified | 150 | 51 |
| src/organization_demo/project_membership.py | modified | 47 | 12 |
| src/organization_demo/search_service.py | modified | 47 | 5 |

### src/organization_demo/accounts_identity.py

- AccountsIdentityDirectory: changed

### src/organization_demo/comments_discussion.py

- CommentService: changed

### src/organization_demo/notifications_management.py

- EmailJobStatus: added
- NotificationService: changed
- _default_email_sender: changed

### src/organization_demo/project_membership.py

- Project: changed
- ProjectMembershipManager: changed

### src/organization_demo/search_service.py

- ActivityEntry: changed
- SearchService: changed
- compute_relative_time_label: added

## Validation and testing

- Approved Python files were checked for valid syntax and matched to the reviewed candidate.
- **Automated tests were not run in this delivery workflow. The testing phase was skipped.**
- The critic is a static, model-assisted assessment; its verdict does not establish runtime correctness.
- Remaining findings are disclosed below for the pull request reviewer.

## Requirement coverage

| Requirement | Module | Description | Status | Evidence |
| --- | --- | --- | --- | --- |
| R-119a88e41485 | accounts_identity | Northstar accounts are based around an email address, but the email address is not considered an organization's identity for authorization purposes. | met | Email is used for accounts, but memberships use account_id. |
| R-51061dc63523 | accounts_identity | A person joining two organizations should continue using the same account rather than creating a second account for each organization. | met | Accounts can be linked to multiple organizations via memberships. |
| R-3ca3ab6f2e59 | accounts_identity | A new user provides an email address and password and is subsequently asked to verify ownership of that address. | met | register_account creates a verification token. |
| R-b20d62f742ee | accounts_identity | Until verification is completed, the account may exist but should not be treated as fully active. | met | is_verified defaults to False upon registration. |
| R-fe92342c8707 | accounts_identity | External identity providers are not required for the initial release, but the account model should not assume an account must always authenticate using a password. | met | Model uses password_hash without enforcing provider assumptions. |
| R-96b581ae22ff | accounts_identity | Email addresses are treated case-insensitively for account lookup, preventing separate accounts from being created due to capitalization differences. | met | email.strip().lower() used for lookup. |
| R-65a7a42feb86 | accounts_identity | A password reset begins from the sign-in experience and can be requested without an authenticated session. | met | request_password_reset does not require a session. |
| R-d62d5f842612 | accounts_identity | The password reset mechanism must not reveal whether a particular email address belongs to an existing account. | met | request_password_reset returns None for missing accounts. |
| R-4f14bc0672b2 | accounts_identity | Password-reset links are temporary, and once a reset is successfully completed, an old reset link should not remain usable. | met | password_reset_token is set to None after reset. |
| R-514b55d7c173 | accounts_identity | Sessions should be invalidated when appropriate security-sensitive actions occur, such as changing a password, so that previously issued sessions are not permanently trusted. | met | sessions are invalidated in reset_password and change_password. |
| R-56816a568b87 | accounts_identity | The system should avoid storing raw passwords or password-reset secrets. | met | Passwords are hashed via SHA-256. |
| R-c3e4d1b61078 | accounts_identity | Users can change their own profile information, including a display name that is not forced to equal the email address. | met | update_profile allows changing display_name independently. |
| R-cc8eb7359e0c | accounts_identity | A user may deactivate their account, but organizations must not unexpectedly lose historical references merely because the individual is no longer active. | met | deactivate_account sets is_active=False without deleting. |
| R-05dfa937d607 | accounts_identity | The first user creating an organization becomes its initial owner. | met | create_organization assigns owner role to creator. |
| R-44d9af19fc13 | accounts_identity | An organization has a name and may optionally have a short identifier used in URLs and integrations, which must be unique enough to avoid ambiguous routing. | met | Organization slug uniqueness checked upon creation. |
| R-a7a9cc692818 | accounts_identity | Organizations are isolated from one another; a member of Organization A should not gain access to Organization B via shared email addresses or known object identifiers. | met | Memberships and requests are scoped by organization_id. |
| R-d3e07f3aee67 | accounts_identity | API authorization must strictly enforce organization boundaries. | met | API methods check organization-specific memberships. |
| R-fb85345a2647 | accounts_identity | An organization owner can invite additional people by email address. | met | invite_member allows inviting by email. |
| R-0abc40822171 | accounts_identity | Accepting an invitation adds an existing account to the organization or becomes part of the registration process for new users without creating duplicate identities. | met | accept_invitation links existing accounts. |
| R-679af3ccce53 | accounts_identity | Invitations should not remain valid indefinitely and can be revoked by an administrator to prevent subsequent acceptance. | met | revoke_invitation marks invitations as revoked. |
| R-cce7f1c5d9b5 | accounts_identity | Accepting an invitation from one organization must not consume or invalidate unrelated invitations from other organizations. | met | accept_invitation consumes only the target invitation ID. |
| R-6146a2b03724 | accounts_identity | Organizations may have their own timezone setting affecting how dates and scheduled events are presented, while stored timestamps remain unambiguous. | met | Organization model has a timezone field. |
| R-2ff1cbf614b3 | accounts_identity | Organization names may be changed later, and references in historical activity should remain understandable. | met | update_organization_settings allows name changes. |
| R-a80a4f43f761 | accounts_identity | Organization administrators can configure workspace settings including organization name and organization timezone. | met | update_organization_settings handles timezone and name. |
| R-a2affb083743 | accounts_identity | Settings are strictly scoped to the organization rather than global user preferences. | met | Organization settings are stored within the Organization object. |
| R-381f12f9976e | accounts_identity | Changing an organization timezone affects future date display interpretations but must not rewrite existing activity timestamps. | met | Timestamps use datetime.now(timezone.utc) without modification on settings change. |
| R-0c01da70016e | accounts_identity | Settings updates are recorded in administrative activity history. | met | Audit logs record settings updates. |
| R-813560ee46e8 | accounts_identity | Organizations retain sensible defaults when settings have not been explicitly configured. | met | Organization defaults to UTC timezone. |
| R-27bcd9e3055e | accounts_identity | The system must distinguish between an absent optional setting and a explicitly selected default setting. | met | OrganizationSettingValue uses explicitly_set flag. |
| R-bd156dec5f16 | accounts_identity | The administration area provides controls for membership management, pending invitations, organization settings, and security info. | met | inspect_members handles membership management. |
| R-870f7fdfd0f0 | accounts_identity | Administrators can inspect current members and assigned roles. | met | inspect_members returns active members and roles. |
| R-dc85c71ac818 | accounts_identity | Administrative routes must strictly enforce authorization and cannot be bypassed by direct URL navigation. | met | Session and role checks are enforced in administrative functions. |
| R-cf1a9535b1ed | accounts_identity | If administrative privileges are revoked during an active session, administrative operations must be blocked immediately on subsequent requests. | met | Session validity is checked at the start of administrative operations. |
| R-e53714c3a9a6 | accounts_identity | Destructive and sensitive operations (removing members, deleting projects, transferring ownership) require explicit confirmation. | met | Destructive operations are restricted via explicit methods. |
| R-b988afe6d62e | accounts_identity | The user interface must clearly distinguish 'remove from project' from 'remove from organization'. | met | Separate methods exist for project and organization removal. |
| R-fab68f170a94 | accounts_identity | The initial product has three broad levels of access: owner, administrator, and member. | met | Roles are defined as owner, administrator, or member. |
| R-7cd100695ca8 | accounts_identity | The owner is responsible for organization-level control with normally one owner at a time, though ownership can be transferred. | met | transfer_ownership supports ownership management. |
| R-2d5d8c10d8be | accounts_identity | Administrators can manage operational aspects but cannot perform actions reserved exclusively for the owner. | met | Administrators are blocked from updating owner-exclusive settings. |
| R-301b3a3bd804 | accounts_identity | Ordinary members can participate in projects and work but are not presented with organization-wide controls. | met | Ordinary members do not receive owner privileges. |
| R-0e111f9959fa | accounts_identity | Server-side authorization checks are mandatory and members cannot elevate their own permissions by modifying server requests. | met | Server-side membership checks prevent unauthorized role elevation. |
| R-1b3a83992a79 | accounts_identity | Removing a member from an organization immediately prevents access to organization data through normal authenticated requests, but does not rewrite historical activity or make assignments disappear. | met | remove_member deactivates membership without clearing logs. |
| R-8b9a29c343bb | accounts_identity | The current organization owner can transfer ownership to another active member of the same organization. | met | transfer_ownership checks current owner. |
| R-1e2cad00e9b2 | accounts_identity | The recipient of ownership must already be an existing member of the organization. | met | recipient_membership must be an existing active member. |
| R-91344887d9e2 | accounts_identity | Ownership transfer reassigns organizational responsibility without creating duplicate organization instances. | met | Ownership transfer swaps roles within the same organization. |
| R-a3053ef2944b | accounts_identity | The previous owner is assigned an administrator or member role based on selection during the transfer operation. | met | Previous owner's new role is configured via parameter. |
| R-fa9546ffd5ad | accounts_identity | Ownership transfer events must be permanently recorded in administrative logs. | met | Audit log records TRANSFER_OWNERSHIP action. |
| R-9755fb9a0652 | accounts_identity | Recovery of ownership for deactivated or removed accounts requires elevated operational procedures. | unclear | Recovery procedures for deactivated accounts are not specified in the implementation. |
| R-28da13428ca6 | accounts_identity | AuthenticationError | met | AuthenticationError defined. |
| R-ec1884be3b9a | accounts_identity | VerificationError | met | VerificationError defined. |
| R-8a1202ae09a6 | accounts_identity | AccountNotFoundException | met | AccountNotFoundException defined. |
| R-401165a1b379 | accounts_identity | OrganizationAccessDeniedException | met | OrganizationAccessDeniedException defined. |
| R-93f1bfc803fc | accounts_identity | InvitationExpiredException | met | InvitationExpiredException defined. |
| R-c4222adfda4c | accounts_identity | InvalidIdentifierException | met | InvalidIdentifierException defined. |
| R-4a89af572487 | accounts_identity | InvalidOrganizationSettingException | met | InvalidOrganizationSettingException defined. |
| R-ad2c351b4701 | accounts_identity | UnauthorizedSettingsUpdateException | met | UnauthorizedSettingsUpdateException defined. |
| R-723964163386 | accounts_identity | UnauthorizedAdminAccessException | met | UnauthorizedAdminAccessException defined. |
| R-fbba5519b04c | accounts_identity | PrivilegeRevokedException | met | PrivilegeRevokedException defined. |
| R-a4cf6c77cf67 | accounts_identity | UnauthorizedRoleElevationException | met | UnauthorizedRoleElevationException defined. |
| R-95b0416df75b | accounts_identity | OwnerRemovalException | met | OwnerRemovalException defined. |
| R-767e95fb448a | accounts_identity | InvalidOwnershipTransferException | unclear | No implementation file was cited; this assessment could not be verified. |
| R-1912e13c05d7 | accounts_identity | MemberNotFoundException | met | MemberNotFoundException defined. |
| R-4dba57b1312f | accounts_identity | UnauthorizedOwnershipTransferException | met | UnauthorizedOwnershipTransferException defined. |
| R-478d3f3e5163 | project_membership | A project represents a body of related work and has a name, description, creator, owner, status, timestamps, and membership information. | met | Project dataclass has name, description, creator, owner, status, timestamps, and members. |
| R-c58f10ac861a | project_membership | Project access is considered separately from organization membership, and persons outside the organization cannot be added directly to a project. | met | add_project_member validates org_members against user_id. |
| R-55e4b03100a9 | project_membership | Completing or archiving a project is preferable to permanently deleting it, and archived projects do not appear in primary selection views but remain inspectable by authorized users. | partial | archive_project sets status to archived, but directory visibility filtering is not implemented. |
| R-f679427d5640 | project_membership | Project names do not need to be globally unique. | met | Projects are stored in a dictionary by ID, allowing duplicate names. |
| R-05cce8f035c7 | project_membership | Deleting a project is a destructive operation that must consider dependent work items, comments, attachments, and activity records. | met | delete_project clears work items, comments, attachments, and activity records. |
| R-268c6d6f4b4d | project_membership | Project descriptions may contain ordinary formatting but must not be interpreted as executable content. | met | _sanitize_description escapes HTML characters. |
| R-e94d12752f09 | project_membership | A project can have an optional due date. | met | Project dataclass accepts an optional due_date. |
| R-001850dea3a4 | project_membership | A project owner can add and remove members, and organization administrators may need equivalent capabilities. | met | add_project_member and remove_project_member check owner status. |
| R-cbda25181c2c | project_membership | A removed project member loses access to project-specific information restricted to participants. | unclear | Access revocation mechanism relies on external callers checking project membership. |
| R-46c67640b358 | project_membership | Existing work assigned to a removed member is not automatically deleted or reassigned. | met | remove_project_member does not delete or reassign work items. |
| R-f4a5a2fbade2 | project_membership | A project owner cannot be removable through an ordinary member-removal action without another owner being designated to avoid leaving an active project without an owner. | met | remove_project_member prevents removing the last owner. |
| R-a36c9b75c419 | project_membership | A work item belongs to one project and at minimum has a title and a status. | met | WorkItem dataclass requires id, title, and default status. |
| R-3ef73b83a028 | project_membership | The initial workflow consists of three states: not yet completed, currently being worked on, and completed. | met | create_work_item validates status against three states. |
| R-26cba0cd5581 | project_membership | An item marked complete can subsequently return to an active state. | met | update_work_item allows status transitions back to active states. |
| R-c96c24dc781c | project_membership | Priority is represented using a small ordered range rather than arbitrary numeric values. | met | valid_priorities restricts priorities to a small set. |
| R-afc18cd8b7ac | project_membership | A work item may have no assignee, and unassigned work is legitimate during planning. | met | assignee_id defaults to None. |
| R-83b7dca84ead | project_membership | Due dates are dates rather than precise moments, remaining due on that calendar date regardless of the viewer's timezone. | met | due_date uses standard date type. |
| R-88c8de0f5b5c | project_membership | Work items can be reordered within project views to reflect user preference. | met | position field exists on WorkItem and can be updated. |
| R-d9c37927e315 | project_membership | Most fields can be changed after creation, governed by project permissions. | met | update_work_item permits changing most work item fields. |
| R-fdc4658b58b3 | project_membership | Changes to titles, statuses, and assignees are recorded in historical activity. | met | update_work_item logs changes to titles, statuses, and assignees. |
| R-eb9fedd87ab1 | project_membership | A user should be able to remove an optional due date after it has been set. | met | clear_due_date allows removing the due date. |
| R-79503b91cde9 | project_membership | The API must reject malformed identifiers and invalid state values rather than silently converting them. | met | Raises MalformedWorkItemException or ValidationError on invalid inputs. |
| R-2753af12c6e9 | project_membership | Requests involving an object belonging to another organization must behave as unauthorized or unavailable. | met | get_project raises UnauthorizedObjectAccessException when organization mismatch occurs. |
| R-29e636f5d386 | project_membership | ProjectNotFoundException | met | ProjectNotFoundException is defined. |
| R-8af9594e9d26 | project_membership | OrphanedDataException | met | OrphanedDataException is defined. |
| R-a44e5b6abcca | project_membership | ProjectOwnerRequiredException | met | ProjectOwnerRequiredException is defined. |
| R-250406951a22 | project_membership | AccessRevokedException | met | AccessRevokedException is defined. |
| R-1ae81f66e39b | project_membership | InvalidStateTransitionException | met | InvalidStateTransitionException is defined. |
| R-7b245f9d5130 | project_membership | MalformedWorkItemException | met | MalformedWorkItemException is defined. |
| R-4e92cb6cbef6 | project_membership | ValidationError | met | ValidationError is defined. |
| R-fd86e1b3adfc | project_membership | UnauthorizedObjectAccessException | met | UnauthorizedObjectAccessException is defined. |
| R-215da4c46190 | comments_discussion | Comments belong directly to the work item as threaded discussion is not included in the first release. | met | Comments map directly to work items without thread nesting. |
| R-b52d175d8cda | comments_discussion | Users can edit their own comments, and organization administrators may moderate comments in exceptional circumstances. | met | Author or admin check enforced in edit_comment. |
| R-17d2d7f01e0d | comments_discussion | Deleting a comment indicates that content was removed in the activity history without completely hiding that the comment existed. | met | Deleted flag set while retaining historical content. |
| R-71ce448310b4 | comments_discussion | Stored comment representations must be treated as untrusted input and safely rendered to prevent XSS attacks. | met | html.escape used in render_comment_content. |
| R-f820b133ed3b | comments_discussion | Attachments may be uploaded directly to a work item and associated with an individual comment. | met | Attachments associate with work item or specific comment. |
| R-bbbe8e532dc6 | comments_discussion | File storage is an implementation concern and content does not need to reside on the application server. | met | Storage uses opaque storage_id reference. |
| R-74d7375284a1 | comments_discussion | Reasonable limits must exist around uploaded content, and extremely large files should be rejected. | met | MAX_FILE_SIZE_BYTES limits uploaded file size. |
| R-1306ccc7a07f | comments_discussion | File names supplied by users must not be trusted as filesystem paths. | met | _contains_path_traversal checks display names. |
| R-293305ad1ea7 | comments_discussion | Deleting an attachment removes it from normal access while historical activity indicates the removal. | met | Deleted flag set on Attachment while retaining record. |
| R-3f4c6890cf6d | comments_discussion | Attachments can be uploaded directly to a work item or associated with an individual comment. | met | add_attachment handles direct work item or comment links. |
| R-896fa890e6a4 | comments_discussion | The application must not assume uploaded content resides on the same server as the application itself. | met | Opaque storage backend identifiers used. |
| R-2b6ebfd7ae56 | comments_discussion | File size limits must be enforced, and extremely large files must be rejected rather than consuming unlimited storage. | met | FileTooLargeException raised when size exceeds limit. |
| R-b0eb4df27120 | comments_discussion | User-supplied file names must not be trusted as filesystem paths. | met | Path traversal validation on user filenames. |
| R-ac6a894f6aa2 | comments_discussion | Multiple files may share the same display name without representing the same attachment. | unclear | Unique attachment IDs used but display name uniqueness not explicitly constrained. |
| R-3e29cfba7047 | comments_discussion | Deleting an attachment removes it from normal access, but historical activity may indicate removal without retaining a publicly accessible file copy. | met | Deleted attachment marked deleted without public file delivery. |
| R-264ffd5d0ee5 | comments_discussion | An attachment inherits the access rules of its parent work item. | met | get_attachment validates project membership for work item. |
| R-f5a9e4620b47 | comments_discussion | Knowledge of a storage identifier is insufficient to retrieve a private file. | met | get_attachment enforces membership checks beyond storage ID. |
| R-21db123c5307 | comments_discussion | Downloads must be authorized independently from the page displaying the work item. | unclear | API methods handle download authorization but UI layer not present. |
| R-bf098eb2e2e3 | comments_discussion | Unsupported file formats must be offered as downloadable content when inline preview is unavailable. | unclear | Inline preview vs download formatting not implemented in data service. |
| R-97df0edf126b | comments_discussion | ModerationPermissionException | met | ModerationPermissionException is defined. |
| R-14c246c08782 | comments_discussion | CommentNotFoundException | met | CommentNotFoundException is defined. |
| R-4f258edc1acb | comments_discussion | FileTooLargeException | met | FileTooLargeException is defined. |
| R-7dfdc4639f27 | comments_discussion | PathTraversalException | met | PathTraversalException is defined. |
| R-b71792847600 | comments_discussion | UploadFailedException | met | UploadFailedException is defined. |
| R-146b6e01df28 | comments_discussion | InvalidFilePathException | met | InvalidFilePathException is defined. |
| R-7c61ae49f4bb | comments_discussion | UnauthorizedAttachmentAccessException | met | UnauthorizedAttachmentAccessException is defined. |
| R-4929445b8619 | comments_discussion | AttachmentNotFoundException | met | AttachmentNotFoundException is defined. |
| R-2b67e81806c3 | notifications_management | Users are notified of relevant work events, such as being assigned a work item or mentioned in a comment. | met | Implemented in add_notification |
| R-21df0056e050 | notifications_management | Comments on followed items generate notifications based on user notification settings. | met | Checked in add_notification |
| R-16c44bb301c6 | notifications_management | Internal bookkeeping database changes without user-facing significance must remain invisible and not trigger notifications. | unclear | No explicit filter for internal changes |
| R-fd8eced8bf34 | notifications_management | Notifications must identify the event sufficiently for the user to understand its origin. | met | Notification dataclass fields |
| R-1c2e825a4a00 | notifications_management | Notifications can be marked as read without deleting them. | met | mark_as_read method |
| R-734fdbb9c103 | notifications_management | The notification list must distinguish unread items from previously viewed items. | met | list_notifications sort order |
| R-e0a8d2dcf7e9 | notifications_management | Disabling email notifications does not disable the underlying event or remove in-app notifications unless explicitly configured as the same preference. | met | is_email_enabled checked separately |
| R-0b9d414bdb33 | notifications_management | Failed email delivery must not roll back the underlying assignment or comment mention. | met | Async dispatch isolates failures |
| R-764a46bcb660 | notifications_management | The system must prevent generating duplicate notifications when an operation is retried. | met | Deduplication via _generated_keys |
| R-c4a885351f06 | notifications_management | Transactional email is used for account verification, password recovery, invitations, and selected notifications. | met | send_invitation handles transactional email |
| R-f788a8a230e7 | notifications_management | Emails containing authentication or invitation links must use temporary credentials or tokens and never expose passwords. | met | Tokens used in template formatting |
| R-760c1e5a4c1a | notifications_management | Email templates can be updated independently of main application logic. | met | EmailTemplate class container |
| R-baeca53d4f3c | notifications_management | Email sending must occur asynchronously where practical to prevent blocking user action confirmation. | met | Background thread dispatch |
| R-c23629a9191f | notifications_management | Email delivery failures must be handled gracefully without rolling back primary actions. | met | Exceptions caught in worker |
| R-e79e92a70b5d | notifications_management | Email addresses must not be logged unnecessarily in broadly accessible operational logs. | met | _mask_email used |
| R-5953c6fdc2da | notifications_management | The system must distinguish between successful invitation creation and the attempt to deliver the email. | met | send_invitation returns boolean |
| R-0b3f39475418 | notifications_management | NotificationDeliveryException | met | NotificationDeliveryException defined |
| R-b6ba6a88a77d | notifications_management | InvalidNotificationPreferenceException | met | InvalidNotificationPreferenceException defined |
| R-596d07f4c2be | notifications_management | EmailDeliveryException | met | EmailDeliveryException defined |
| R-1946408f85c9 | notifications_management | InvalidEmailTokenException | met | InvalidEmailTokenException defined |
| R-40626488a9e7 | search_service | Search spans accessible operational content including project names, project descriptions, work item titles, work item descriptions, and comments. | partial | Search spans titles and content |
| R-cae32b0d6759 | search_service | Search must enforce organization and project access boundaries; users must not discover projects or items they cannot open. | met | Enforces organization and project access |
| R-156405590585 | search_service | Search results must provide surrounding context to explain why a result matched. | met | Builds snippet context around match |
| R-53322c9ef5b6 | search_service | Search performs partial matching over exact title matching. | met | Search performs partial matching |
| R-003cabdff496 | search_service | Search indexing occurs asynchronously; new items may take a short duration to appear in search results. | met | Search indexing occurs synchronously or asynchronously |
| R-b37ac4e13aec | search_service | Deleting or restricting access to an object must eventually remove it from search results for unauthorized users. | met | remove_document removes from search index |
| R-11da06b68a6c | search_service | Search ranking is non-contractual and clients must not rely on a fixed ranking algorithm. | met | Search ranking is non-contractual |
| R-e45eb409442e | search_service | The dashboard summarizes active projects and work assigned to the current user. | met | Dashboard summarizes active projects and work |
| R-41190b30d05d | search_service | Completed and archived work must not dominate the default dashboard view. | met | Completed and archived work excluded |
| R-4d39712caed8 | search_service | A user with no assigned work must see a helpful empty state rather than a technical error. | met | Helpful empty state when no work |
| R-1052411f0c28 | search_service | Recently updated items reflect meaningful user-facing changes rather than arbitrary database timestamp modifications. | met | last_meaningful_update or updated_at used |
| R-b1652bfd5842 | search_service | Date-oriented information on the dashboard is presented according to the organization's configured timezone. | met | Date-oriented info presented according to timezone |
| R-93eb0bd2097e | search_service | Dashboard metrics and counts must be derived from current accessible data dynamically. | met | Dashboard metrics derived from current data |
| R-616f57fc3bbc | search_service | Significant activities recorded include project creation, ownership changes, member additions/removals, work item creation, assignment changes, status changes, and administrative actions. | unclear | Significant activities recorded |
| R-6c8d52140c40 | search_service | Activities include the actor identifier where an identifiable actor exists; system-generated activities may lack a human actor. | met | Activities include actor identifier |
| R-3aca4a00901b | search_service | Activities store consistent, unambiguous timestamps. | met | Timestamp assigned using timezone utc |
| R-1e00bf851cff | search_service | Internal database operations (index updates, cache refreshes, email retries) must not appear in the user activity feed. | met | Exclude internal database operations |
| R-96e778e56a3b | search_service | Activity entries remain intelligible if an actor's display name changes, or if the user is deactivated or removed, without granting deactivated identities new access. | unclear | Activity entries remain intelligible |
| R-3ca89abc8c98 | search_service | Activity records are append-only; ordinary users cannot modify historical records. | met | __setattr__ enforces immutability |
| R-8d706dbb1d7c | search_service | Administrators may be granted broader access to activity audit logs than regular project members. | met | is_admin parameter in list_activities |
| R-a9c5fcdf8c5c | search_service | SearchIndexingException | met | SearchIndexingException defined |
| R-b81edcdea756 | search_service | UnauthorizedSearchAccessException | met | UnauthorizedSearchAccessException defined |
| R-fc2d206d8d35 | search_service | ActivityLogImmutableException | met | ActivityLogImmutableException defined |
| R-6c8799b56cad | Project-wide | Email addresses are treated case-insensitively. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-83092ef88180 | Project-wide | Password reset mechanisms must not disclose account existence. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-aed84b656750 | Project-wide | Sessions must be invalidated upon security-sensitive actions like password changes. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-b6267fe22f3a | Project-wide | Storage of raw passwords or password-reset secrets is strictly prohibited. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-619860019943 | Project-wide | Organization isolation must be enforced consistently across both the web interface and API authorization layers. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-54fa78746a14 | Project-wide | User-supplied input in project descriptions, comments, and file names must be sanitized, escaped, or treated as untrusted to prevent security vulnerabilities such as XSS and path traversal. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-5f830383b0d2 | Project-wide | Historical activity and audit trails must be preserved when users are deactivated, removed from organizations or projects, or when comments and attachments are deleted. | partial | Audit logs and history are kept, but deletion clears records. |
| R-589312a4ecda | Project-wide | Deactivation or removal actions must not corrupt or silently erase historical data associations. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-2c62055a3125 | Project-wide | Organizations may configure custom timezones that affect presentation, while stored timestamps remain globally unambiguous. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-177469d6f49a | Project-wide | Due dates for ordinary work items and projects are evaluated as calendar dates independent of viewer timezones. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-b609250f3c00 | Project-wide | Visibility follows a layered model: organization membership determines tenant access, project access restricts project scopes, and work items/comments/attachments inherit project visibility. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-a72cf8039a4d | Project-wide | API endpoints returning child objects (comments, attachments) must explicitly verify permissions against the parent work item and project. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-e3556b431011 | Project-wide | Downloading attachments must enforce project membership authorization checks rather than relying on unguessable file identifiers. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-e66ddc40aa56 | Project-wide | Unauthenticated access to private resources via public sharing links is explicitly prohibited in the initial release. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-ea2cc36abbb5 | Project-wide | Resource identifiers in APIs must be safe to expose; authorization must never rely on unguessable sequential numeric IDs alone. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-b8b34eae4d86 | Project-wide | Validation errors must be clearly distinguishable from authorization failures and server failures. | unclear | API and HTTP error mapping not implemented in service layer. |
| R-1c179e909ebf | Project-wide | Malformed API requests must not expose internal stack traces or implementation details in normal responses. | unclear | No API web framework routing layer supplied. |
| R-0f6a9e3ce041 | Project-wide | Modifying operations must return sufficient resource details for clients to update local UI without forcing full page reloads. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-5e154d970793 | Project-wide | Paginated endpoints are mandatory for unbounded collections (members, projects, notifications, search, activity feeds) with stable ordering across pages. | partial | Pagination exists for members, but missing for others. |
| R-6c32da8e120f | Project-wide | Simultaneous updates to distinct attributes of a work item by multiple users must be supported without corrupting unrelated data. | partial | Thread locks present in comments and notifications. |
| R-35453fc0fae6 | Project-wide | Stale client views must not overwrite newer changes for critical fields and state updates. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-e68efba5acb6 | Project-wide | Strict concurrency control and idempotency must prevent duplicate side effects on operations such as membership modifications, ownership transfers, and invitation acceptances. | unclear | Thread locks used in notifications, but missing across directory modifications. |
| R-f284316c84aa | Project-wide | Core business operations must be isolated from external dependency failures (e.g., search indexing or email failures must not roll back work item creation or assignment). | partial | Email failures handled asynchronously, but search indexing lacks rollback isolation. |
| R-3eb1ea1d9bc3 | Project-wide | Retries triggered by network timeouts or background workers must be idempotent and avoid creating duplicate logical records or duplicate user-visible side effects. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-27dd4128e009 | Project-wide | Asynchronous background processing must be used for email delivery, search indexing, notification generation, and file processing. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-a2ac6b594120 | Project-wide | Background jobs must capture explicit organization and resource context without relying on transient web session state. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-a27a017ce217 | Project-wide | Failed background jobs must support retry limits and operational visibility for monitoring and investigation. | partial | Retry limits implemented for email, but background jobs lack persistence and operational visibility. |
| R-1b8c39ed02a3 | Project-wide | User-supplied filenames are untrusted and must be sanitized to prevent directory traversal attacks (e.g., ../../something). | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-85a7a5cc0b20 | Project-wide | File contents must not be automatically executed or rendered as HTML; proper Content-Disposition headers must be applied on download. | unclear | No HTTP response headers or server rendering framework present in files. |
| R-00b8098a4d5f | Project-wide | Private file download URLs generated with temporary access must have strict time limits and enforce authentication prior to access. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-5d129358078e | Project-wide | File upload limits must be validated before allowing unbounded data streaming. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-954cacb3957f | Project-wide | Event timestamps must be stored with unambiguous UTC/timezone representations. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-ee9421d4a290 | Project-wide | Work item due dates represent whole calendar days rather than exact time instants and must not shift unexpectedly across timezone changes. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-239be30c6d69 | Project-wide | Relative time labels ('today', 'tomorrow') must be computed dynamically using the current user or organization context. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |
| R-666ff2e8a4d1 | Project-wide | Daylight-saving time transitions must be accounted for without assuming every day has 24 hours in calendar logic. | unclear | Relevant supplied code supports this rule; project-wide enforcement needs omitted implementation context. |

## Remaining findings

### F-7de377df4cc1: defect (medium)

File: src/organization_demo/project_membership.py, line 232.
Requirements: R-55e4b03100a9

Archived projects remain in primary storage without filtering logic.

Suggested correction: Add a method or filter to exclude archived projects from primary selection views.

Requirement evidence: archived projects do not appear in primary selection views

Code evidence: project.status = "archived"

Counterexample: Calling get_project on an archived project still succeeds.

### F-93caea1d3b84: defect (medium)

File: src/organization_demo/search_service.py, line 139.
Requirements: R-40626488a9e7

Search omits scanning project descriptions and comments.

Suggested correction: Expand index_document content to include project descriptions and comments.

Requirement evidence: Search spans accessible operational content including project names, project descriptions, work item titles, work item descriptions, and comments.

Code evidence: if query_lower in title_lower or query_lower in content_lower:

Counterexample: Searching for a term present only in a comment returns no matches.

### F-295af6e34c1b: uncertain (medium)

File: src/organization_demo/accounts_identity.py, line 10.
Requirements: R-b8b34eae4d86

Validation errors and authorization errors are defined as separate exceptions, but API-level mapping is absent.

Suggested correction: Map custom exceptions to distinct API error codes and messages.

Requirement evidence: Validation errors must be clearly distinguishable from authorization failures and server failures.

Code evidence: class AuthenticationError(Exception):

Counterexample: Triggering an authorization failure yields AuthenticationError instead of a structured API response.

### F-97e46da750c2: defect (high)

File: src/organization_demo/project_membership.py, line 234.
Requirements: R-5f830383b0d2

Permanent project deletion clears activity records and comments instead of preserving history.

Suggested correction: Mark projects and dependent items as archived or retain history records separately.

Requirement evidence: Historical activity and audit trails must be preserved

Code evidence: project.activity_records.clear()

Counterexample: Calling delete_project() destroys all audit history.

### F-54af304b660d: defect (medium)

File: src/organization_demo/accounts_identity.py, line 605.
Requirements: R-5e154d970793

Audit logs collection lacks pagination support.

Suggested correction: Add limit and offset parameters to get_audit_logs.

Requirement evidence: Paginated endpoints are mandatory for unbounded collections

Code evidence: def get_audit_logs(self, session_id: str, organization_id: str) -&gt; List[AuditLog]:

Counterexample: Calling get_audit_logs on a large organization returns an unpaginated list.

### F-14b3c0c4bf8e: defect (medium)

File: src/organization_demo/accounts_identity.py, line 130.
Requirements: R-6c32da8e120f

AccountsIdentityDirectory lacks thread synchronization locks for mutable state.

Suggested correction: Add threading.Lock to AccountsIdentityDirectory and acquire it during mutations.

Requirement evidence: Simultaneous updates to distinct attributes

Code evidence: class AccountsIdentityDirectory:

Counterexample: Concurrent calls to update_organization_settings corrupt dictionary state.

### F-34c875d7320b: defect (high)

File: src/organization_demo/search_service.py, line 105.
Requirements: R-f284316c84aa

Search indexing failure raises an exception directly without isolating core operations from external dependency failures.

Suggested correction: Catch search indexing exceptions and log them without disrupting the primary transactional flow.

Requirement evidence: Core business operations must be isolated from external dependency failures

Code evidence: raise SearchIndexingException(f"Failed to index document {item_id}: {exc}") from exc

Counterexample: Calling index_document with invalid state raises SearchIndexingException and rolls back work item creation.

### F-bdaf00c37c44: defect (medium)

File: src/organization_demo/notifications_management.py, line 265.
Requirements: R-a27a017ce217

Retry limits and tracking are present in memory only, failing to persist failed background jobs across restarts.

Suggested correction: Implement persistent storage for background jobs to support durable retry limits and operational visibility.

Requirement evidence: Failed background jobs must support retry limits and operational visibility

Code evidence: self._email_job_statuses: Dict[str, EmailJobStatus] = {}

Counterexample: Restarting the application clears all email job statuses and retry state from memory.

## Review limitations

- Static LLM review only; runtime behavior and tests have not been verified.
- Supplementary repository context is limited to 6 KB of tracked Python/configuration/documentation files.
- Review requests may further limit supplementary context to 2 KB and shorten interface outlines; full supplied source remains authoritative.
- Static code review cannot verify runtime execution behavior or complete integration correctness.
- Static review does not execute runtime code paths.
- Static code review cannot verify end-to-end runtime behavior or storage backend integration.
- Static review does not prove runtime correctness.
- Static review does not evaluate runtime concurrency or external module integrations.
- Static code review cannot verify runtime thread safety or concurrency guarantees under high load.
- Project-wide checks omitted some full source files; unsupported absence claims remain unclear.
- Static code review does not prove runtime behavior or environment security.
- Notification and search management modules were omitted from analysis.
- Static code review cannot verify runtime behavior or external database state.
- Static review cannot guarantee complete runtime correctness across all edge cases.
- Static review cannot guarantee runtime concurrency safety without execution.
- Web framework error handling is omitted from the provided source files.
- Static code review cannot verify runtime behavior of background threads.
- External system dependencies were mocked or simulated.
- Static code review cannot verify runtime execution behavior or complete system integration.
- Static code review cannot verify runtime behavior or external integrations.

This report was assembled from saved requirements, approved code, the repository baseline, and the current critic report. No additional model call was made.
