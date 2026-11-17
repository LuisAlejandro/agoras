Changelog
============


3.0.1 (2026-11-17)
------------

Other
~~~~~~~~~~~~

* Chore(deps): update python-telegram-bot requirement from >=22.1 to >=22.8 in /packages/platforms. [Luis Alejandro Martínez Faneyth]

* Chore(deps): bump google-auth-httplib2 from 0.4.1 to 0.4.2 in /packages/platforms. [Luis Alejandro Martínez Faneyth]

* Chore(deps): regenerate root dependency files after develop merge. [Luis Alejandro Martínez Faneyth]

* Align google-auth to 2.58.0 across platforms and root setup. [Cursor Agent]

* Chore(deps): align cryptography>=50.0.1 in setup.py and root deps. [Cursor Agent]

* Chore(deps): sync root setup.py and requirements.txt for google-api-python-client 2.200.0. [Cursor Agent]

* Fix(ci): sync urllib3 bump in setup.py via sync_package_deps. [Cursor Agent]

* Chore(deps): sync google-api-python-client 2.200.0 in platforms package. [Cursor Agent]

* Chore(deps): bump cryptography to >=50.0.1 in platforms setup.py. [Cursor Agent]


3.0.0 (2026-11-17)
------------

Added
~~~~~~~~~~~~

* E2E: media replies, list-posts verify, and X thread in unattended suites. [Luis Alejandro Martínez Faneyth]

* Document LinkedIn scope override and two-app authorize model. [Luis Alejandro Martínez Faneyth]

* LinkedIn authorize --scope flag plumbing with env-safe scope key. [Luis Alejandro Martínez Faneyth]

* LinkedIn authorize --scope override with sign-in default scopes. [Luis Alejandro Martínez Faneyth]

* Fail CI when package dependencies drift out of sync. [Luis Alejandro Martínez Faneyth]

* Wrapper-to-api seam integration tests (U5) [Luis Alejandro Martínez Faneyth]

* Reply media backends, delete-reply, and E2E reply-cycle tests. [Luis Alejandro Martínez Faneyth]

* Instagram media delete support. [Luis Alejandro Martínez Faneyth]

* Resolve LinkedIn read media URNs and sanitize Discord read errors. [Luis Alejandro Martínez Faneyth]

* Get-post and get-reply read actions across networks. [Luis Alejandro Martínez Faneyth]

* Media-capable reply action across networks. [Luis Alejandro Martínez Faneyth]


Changed
~~~~~~~~~~~~

* Stored credentials must be re-authorized once after upgrade. [Luis Alejandro Martínez Faneyth]

* Poll remote media status through one bounded helper. [Luis Alejandro Martínez Faneyth]

* Give media, auth, and clients one explicit state each. [Luis Alejandro Martínez Faneyth]

* Share one runner across CLI platform commands. [Luis Alejandro Martínez Faneyth]

* Table-drive wrapper like, share, and delete handlers. [Luis Alejandro Martínez Faneyth]

* Share credential, authorize, and main-shim wrapper plumbing. [Luis Alejandro Martínez Faneyth]

* Share one driver across the platform-parity verify gates. [Luis Alejandro Martínez Faneyth]

* Share API post-auth and disconnect hooks across platforms. [Luis Alejandro Martínez Faneyth]

* Collapse legacy publish stub to one exit path. [Luis Alejandro Martínez Faneyth]

* Lint: import sorting on normalized api modules. [Luis Alejandro Martínez Faneyth]

* Normalize x/discord/telegram guards to ensure dialect (U4) [Luis Alejandro Martínez Faneyth]

* Fix bare-root pytest collection via package chain (U1) [Luis Alejandro Martínez Faneyth]

* Selectable credential profiles via app@account composite keys. [Luis Alejandro Martínez Faneyth]

* Composite profile key in core token storage. [Luis Alejandro Martínez Faneyth]


Fixed
~~~~~~~~~~~~

* Report terminal states instead of collapsing them. [Luis Alejandro Martínez Faneyth]

* Migrate Discord invite links to Luis Develops Community. [Luis Alejandro Martínez Faneyth]

* Restore package version to 2.2.0 after premature 3.0.0 bump. [Luis Alejandro Martínez Faneyth]

* TikTok authorize sends comma-separated scopes to the consent URL. [Luis Alejandro Martínez Faneyth]

* Threads authorize accepts numeric user_id from Meta token responses. [Luis Alejandro Martínez Faneyth]

* List-posts: LinkedIn q=author finder, Facebook deprecated attachment field, object-id + retry in E2E helper. [Luis Alejandro Martínez Faneyth]

* X list-posts uses OAuth1 user context (user_auth) so timeline reads work. [Luis Alejandro Martínez Faneyth]

* Clear X list-posts error when timeline read is gated by API tier. [Luis Alejandro Martínez Faneyth]

* Reply-cycle YouTube upload uses unlisted privacy so comments are allowed. [Luis Alejandro Martínez Faneyth]

* Document like as Community-Management-gated LinkedIn action. [Luis Alejandro Martínez Faneyth]

* Keep object-id canonical for LinkedIn authorize identity to avoid composite drift. [Luis Alejandro Martínez Faneyth]

* Restore w_member_social posting default and id_token identity for LinkedIn authorize. [Luis Alejandro Martínez Faneyth]

* QA: stop echoing tokens on authorize and drop redundant env keys. [Luis Alejandro Martínez Faneyth]

* QA: correct README import paths and drop dead helper return. [Luis Alejandro Martínez Faneyth]

* QA findings on remaining-cleanup-tail: X ensure, reply guards, shared fakes. [Luis Alejandro Martínez Faneyth]

* Harden credential-profile selection edge cases. [Luis Alejandro Martínez Faneyth]


Removed
~~~~~~~~~~~~

* Stop automatic pull request merges. [Luis Alejandro Martínez Faneyth]

* Remove dead sheet, feed, media and CLI code paths. [Luis Alejandro Martínez Faneyth]

* Remove deprecated credential forwarders (U3) [Luis Alejandro Martínez Faneyth]

* Remove test-only delete_token and int timestamp compares (U2) [Luis Alejandro Martínez Faneyth]


Other
~~~~~~~~~~~~

* Fix(common): remove unused os import in version.py. [Cursor Agent]

* Docs: ci probe for Cursor auto-approve pipeline. [Luis Alejandro Martínez Faneyth]

* Test. [Luis Alejandro Martínez Faneyth]

* Docs: apply docs-loop audit fixes. [Luis Alejandro Martínez Faneyth]

* Docs: apply docs-loop audit fixes. [Luis Alejandro Martínez Faneyth]

* Docs: apply docs-loop audit fixes. [Luis Alejandro Martínez Faneyth]

* Docs: apply docs-loop audit fixes. [Luis Alejandro Martínez Faneyth]

* Docs: apply docs-loop audit fixes. [Luis Alejandro Martínez Faneyth]

* Refactor: derive LinkedIn --scope help default from auth constant. [Luis Alejandro Martínez Faneyth]

* Chore(scripts): remove obsolete artifacts (R5) [Luis Alejandro Martínez Faneyth]

* Refactor(platforms): collapse duplicate upload-timeout helpers (R4) [Luis Alejandro Martínez Faneyth]

* Refactor(core): neutralize schedule hour format round-trip (R3) [Luis Alejandro Martínez Faneyth]

* Refactor(common): replace hand-rolled level map with stdlib (R2) [Luis Alejandro Martínez Faneyth]

* Refactor(media): MediaFactory class becomes module functions (R1) [Luis Alejandro Martínez Faneyth]

* Fix(core,platforms,scripts,tests): address QA residuals round 2. [Luis Alejandro Martínez Faneyth]

* Fix(tests,docs,scripts): QA findings on chunk-B branch. [Luis Alejandro Martínez Faneyth]

* Feat(scripts,ci): vulture dead-code gate (R7, R8) [Luis Alejandro Martínez Faneyth]

* Refactor(cli): remove dead content-spec constants (R6) [Luis Alejandro Martínez Faneyth]

* Refactor(cli): remove unread registry metadata and get_platform_info (R5) [Luis Alejandro Martínez Faneyth]

* Refactor(core)!: remove unconsumed re-export layers (R4) [Luis Alejandro Martínez Faneyth]

* Refactor(cli,core,platforms)!: delete 11 dead platform and base methods (R3) [Luis Alejandro Martínez Faneyth]

* Refactor(core): delete managers part 2 — sheet/feed dead methods, tests, README (R1, R2) [Luis Alejandro Martínez Faneyth]

* Refactor(core,docs)!: delete FeedManager and SheetManager (R1) [Luis Alejandro Martínez Faneyth]

* Test: stabilize discord asyncio suite under full platforms run. [Cursor Agent]

* Fix(platforms,core,common): QA wave-3 findings (surface, encoding, contracts) [Luis Alejandro Martínez Faneyth]

* Fix(core,platforms,common): QA findings on chunk A. [Luis Alejandro Martínez Faneyth]

* Chore(deps): remove seven dependency pins and regenerate (R1-R5, R11) [Luis Alejandro Martínez Faneyth]

* Refactor(platforms): tiktok/instagram retry loops to urllib3 Retry (R7) [Luis Alejandro Martínez Faneyth]

* Fix(platforms): drop unused http.client import after retry swap. [Luis Alejandro Martínez Faneyth]

* Refactor(platforms): youtube upload retry to googleapiclient num_retries (R7) [Luis Alejandro Martínez Faneyth]

* Refactor(platforms): replace hand-rolled AuthorizedHttp with google_auth_httplib2 (R6) [Luis Alejandro Martínez Faneyth]

* Refactor(common): replace beautifulsoup4 metatag scan with stdlib HTMLParser (R10) [Luis Alejandro Martínez Faneyth]

* Refactor(core): replace dateutil with stdlib datetime in schedule (R9) [Luis Alejandro Martínez Faneyth]

* Refactor(core): replace atoma RSS parser with stdlib (R8) [Luis Alejandro Martínez Faneyth]

* Fix(core,scripts,docs): QA round 2 on decorator-residuals branch. [Luis Alejandro Martínez Faneyth]

* Fix(core,scripts,tests): QA findings on decorator-residuals branch. [Luis Alejandro Martínez Faneyth]

* Feat(scripts): api rate-limit parity gate (R8) [Luis Alejandro Martínez Faneyth]

* Test(platforms): wrapper token-leak tests (R12) [Luis Alejandro Martínez Faneyth]

* Fix(core,platforms): sanitize and sever wrapper re-chain sites (R11) [Luis Alejandro Martínez Faneyth]

* Fix(core): serialize auto-auth first call and rate-limit buckets (R9, R10) [Luis Alejandro Martínez Faneyth]

* Test(core,platforms): pin five unpinned guard behaviors (R3-R7) [Luis Alejandro Martínez Faneyth]

* Fix(core): sanitized fail-safe raise in guard_error_wrap (R2) [Luis Alejandro Martínez Faneyth]

* Refactor(core): type guard decorators against bound GuardableAPI protocol. [Luis Alejandro Martínez Faneyth]

* Docs(migration): flip remaining present-tense publish references. [Luis Alejandro Martínez Faneyth]

* Fix(cli,docs,tests): address QA findings on legacy publish removal. [Luis Alejandro Martínez Faneyth]

* Style(cli): isort import order in main entry. [Luis Alejandro Martínez Faneyth]

* Release: bump version to 3.0.0 (U5) [Luis Alejandro Martínez Faneyth]

* Fix(cli): absorb arbitrary legacy args in the publish stub; finish test deletions. [Luis Alejandro Martínez Faneyth]

* Docs(cli): flip publish references from deprecated to removed in 3.0 (U4) [Luis Alejandro Martínez Faneyth]

* Test(cli): remove legacy publish tests, add stub tests, trim mixed files (U3) [Luis Alejandro Martínez Faneyth]

* Refactor(cli): trim legacy conversion surface from converter (U2) [Luis Alejandro Martínez Faneyth]

* Refactor(cli): remove legacy agoras publish command, add pointer stub (U1) [Luis Alejandro Martínez Faneyth]

* Fix(core,scripts,tests): close #769 QA residuals — redaction, guard-order gate, discord flake. [Luis Alejandro Martínez Faneyth]

* Test(platforms,scripts): close QA residuals on wrapper skeleton hoist. [Luis Alejandro Martínez Faneyth]

* Fix(core,platforms): QA findings on wrapper skeleton hoist. [Luis Alejandro Martínez Faneyth]

* Feat(platforms): migrate 9 wrappers to base skeleton (U3-U5) [Luis Alejandro Martínez Faneyth]

* Feat(x): migrate wrapper to base skeleton (U2 pilot) [Luis Alejandro Martínez Faneyth]

* Feat(core): hoist wrapper skeleton into SocialNetwork base (U1) [Luis Alejandro Martínez Faneyth]

* Fix(core): avoid Bandit B107 on guard_token_presence default. [Cursor Agent]

* Fix(core,platforms): QA round 2 — redaction, disconnect, deprecated forwarders. [Luis Alejandro Martínez Faneyth]

* Fix(core): guard_token_presence degrades missing manager to not-authenticated. [Luis Alejandro Martínez Faneyth]

* Fix(platforms): address QA findings on guard decorator refactor. [Luis Alejandro Martínez Faneyth]

* Test(platforms): pin not-supported guard-skip (U9) [Luis Alejandro Martínez Faneyth]

* Refactor(core,platforms): dedupe authenticate/disconnect into base (U7) [Luis Alejandro Martínez Faneyth]

* Refactor(platforms): delete credential property forwarders (U6) [Luis Alejandro Martínez Faneyth]

* Feat(threads,whatsapp,youtube): migrate api to guard decorators (U8) [Luis Alejandro Martínez Faneyth]

* Feat(facebook,instagram,linkedin): migrate api to guard decorators (U5) [Luis Alejandro Martínez Faneyth]

* Feat(x): migrate api to guard decorators (U4 assert dialect) [Luis Alejandro Martínez Faneyth]

* Feat(discord,telegram): migrate api to guard decorators (U4) [Luis Alejandro Martínez Faneyth]

* Feat(tiktok): migrate api to composable guard decorators. [Luis Alejandro Martínez Faneyth]

* Feat(core): composable guard decorators for platform api operations. [Luis Alejandro Martínez Faneyth]

* Docs(audit): guard-composition inventory for platform api refactor. [Luis Alejandro Martínez Faneyth]

* Test(platforms): update Instagram API delete test for media delete support. [Cursor Agent]

* Fix(tests): update Instagram API delete test for media delete support. [Cursor Agent]

* Update. [Luis Alejandro Martínez Faneyth]

* Test(platforms): update Instagram API delete test for media delete support. [Cursor Agent]


2.2.0 (2026-08-26)
------------

Added
~~~~~~~~~~~~

* Instagram local video via rupload. [Luis Alejandro Martínez Faneyth]

* Local file and file:// media support. [Luis Alejandro Martínez Faneyth]


Changed
~~~~~~~~~~~~

* Request TikTok video.publish OAuth scopes. [Luis Alejandro Martínez Faneyth]


Other
~~~~~~~~~~~~

* Fix: ruff format upload_resumable_video signature. [Cursor Agent]

* Fix(ci): satisfy Ruff format and Bandit B113 on local media upload paths. [Cursor Agent]

* Merge develop into feature/local-media-support. [Luis Alejandro Martínez Faneyth]


2.1.2 (2026-08-25)
------------

Added
~~~~~~~~~~~~

* Share-to-TikTok composer for interactive posts. [Luis Alejandro Martínez Faneyth]


Other
~~~~~~~~~~~~

* Fix TikTok composer lint, Semgrep, and Pyright for PR CI. [Cursor Agent]


2.1.1 (2026-08-14)
------------

Fixed
~~~~~~~~~~~~

* Fetch X Premium tier live at post time. [Luis Alejandro Martínez Faneyth]

* Cut release artifact retention to 30 days; add cache purge. [Luis Alejandro Martínez Faneyth]

* Rename root dist to agoras-meta and ship text_limits data file. [Luis Alejandro Martínez Faneyth]


Other
~~~~~~~~~~~~

* Chore(deps): sync Pillow>=12.3.0 across packages via sync_package_deps. [Cursor Agent]

* Fix(deps): sync google-auth 2.56.3 across packages after core bump. [Cursor Agent]

* Align google-auth to 2.56.3 across all packages. [Cursor Agent]

* Fix(platforms): cast OAuth1Session for mount() under pyright 1.1.411. [Cursor Agent]

* Chore(deps): align google-auth 2.56.2 across packages/platforms and root. [Cursor Agent]


2.1.0 (2026-08-07)
------------

Added
~~~~~~~~~~~~

* YAML content files and native threads. [Luis Alejandro Martínez Faneyth]

* Document gitchangelog commit tags in MAINTAINER. [Luis Alejandro Martínez Faneyth]


Fixed
~~~~~~~~~~~~

* Retry transient GitHub API errors in PR auto-merge. [Luis Alejandro Martínez Faneyth]

* Use top-level getOctokit in pr-auto-merge updateBranch step. [Luis Alejandro Martínez Faneyth]


Other
~~~~~~~~~~~~

* Fix(core): align google-auth with platforms bump to 2.56.2. [Cursor Agent]

* Fix(x): drop duplicate tweet validation after rebase. [Luis Alejandro Martínez Faneyth]

* Fix(tiktok): initialize tiktok_description in __init__ for text validation. [Cursor Agent]

* Style: apply Ruff format to text_limits module. [Cursor Agent]

* Fix: address QA review for text-limit rejection. [Luis Alejandro Martínez Faneyth]

* Feat(core): reject posts that exceed platform text limits. [Luis Alejandro Martínez Faneyth]

* Upgrade PR auto-merge to SHA-bound native-first controller. [Luis Alejandro Martínez Faneyth]

* Fix(deps): align google-auth 2.56.0 across core and root packages. [Cursor Agent]

* Fix(deps): sync google-auth 2.56.0 across platforms and root. [Cursor Agent]

* Fix: replace deluser/delgroup with userdel/groupdel in Dockerfiles. [Luis Alejandro Martínez Faneyth]

* Chore: apply rosey-maintainer fleet sync. [Luis Alejandro Martínez Faneyth]

* Chore: update gitignore. [Luis Alejandro Martínez Faneyth]

* Update. [Luis Alejandro Martínez Faneyth]

* Fix(deps): pin sphinx by Python version for unit test matrix. [Cursor Agent]

* Fix(core): align google-auth with platforms bump to 2.55.1. [Cursor Agent]

* Fix(platforms): align google-auth 2.55.1 with core for Dependabot bump. [Cursor Agent]

* Fix: propagate access_token to LinkedInAPI and update Instagram docs. [Luis Alejandro Martínez Faneyth]

* Feat: support LinkedIn standard app access-token-only authorization. [Luis Alejandro Martínez Faneyth]

* Test: update Telegram invalid-token test for AuthenticationError. [Cursor Agent]

* Fix: skip auto-merge for draft pull requests. [Luis Alejandro Martínez Faneyth]

* Fix: refresh and sync unattended test tokens after live runs. [Luis Alejandro Martínez Faneyth]

* Fix: surface categorized auth failures on CLI authenticate path. [Luis Alejandro Martínez Faneyth]

* Chore: maintainer sync follow-ups for docs and Makefile. [Luis Alejandro Martínez Faneyth]

* Chore: sync maintainer ops from rosey-maintainer-sync. [Luis Alejandro Martínez Faneyth]

* Chore: sync maintainer ops from fleet-wide rosey-maintainer-sync. [Luis Alejandro Martínez Faneyth]

* Refactor: consolidate lint and format on Ruff. [Luis Alejandro Martínez Faneyth]

* Chore: sync maintainer release preflight and ops tooling. [Luis Alejandro Martínez Faneyth]

* Feat: 2.1.0 utils authorize-only and platform runner dispatch. [Luis Alejandro Martínez Faneyth]

* Formatting nits. [Luis Alejandro Martínez Faneyth]


2.0.5 (2026-06-24)
------------

Other
~~~~~~~~~~~~

* Updating readthedocs generation. [Luis Alejandro Martínez Faneyth]


2.0.4 (2026-06-24)
------------

Other
~~~~~~~~~~~~

* Updating readthedocs generation. [Luis Alejandro Martínez Faneyth]


2.0.3 (2026-06-23)
------------

Other
~~~~~~~~~~~~

* Chore: export BASH_ENV in Makefile for bash recipe env. [Luis Alejandro Martínez Faneyth]

* Solving bumpversion multiline issue. [Luis Alejandro Martínez Faneyth]

* Chore: sync maintainer ops and inline post_bump_commands parser. [Luis Alejandro Martínez Faneyth]

* Test(common): ignore pytest logging handlers in logger tests. [Cursor Agent]

* Chore: sync maintainer release scripts and CI workflows. [Luis Alejandro Martínez Faneyth]

* Chore(deps-dev): bump pytest-asyncio to 1.4.0 for pytest 9.x compatibility. [Cursor Agent]

* Improving dependency resolution robustness. [Luis Alejandro Martínez Faneyth]


2.0.2 (2026-06-23)
------------

Other
~~~~~~~~~~~~

* Chore: sync MAINTAINER CI notes and lib.sh manifest to 0.4.3. [Luis Alejandro Martínez Faneyth]

* Chore: maintainer sync toolkit 0.4.3. [Luis Alejandro Martínez Faneyth]

* Chore: maintainer sync toolkit 0.4.2 — PR CI + auto-merge. [Luis Alejandro Martínez Faneyth]

* Fix(core): align google-auth with platforms bump to 2.55.0. [Cursor Agent]

* Chore: remove CI probe v10 marker from MAINTAINER. [Luis Alejandro Martínez Faneyth]

* Fix(ci): safe.directory for Semgrep dispatch git fetch in container. [Luis Alejandro Martínez Faneyth]

* Chore: retrigger PR CI after probe fix. [Cursor Agent]

* Fix(ci): remove intentional probe test failure (v6) [Cursor Agent]

* Fix(ci): repair pr-auto-merge actor gate YAML folding. [Luis Alejandro Martínez Faneyth]

* Simplify PR CI: embed Semgrep in pr.yml, drop code-quality workflow. [Luis Alejandro Martínez Faneyth]

* Test: remove CI auto-merge probe v4 (fix intentional failure) [Cursor Agent]

* Test: CI auto-merge probe v4 (intentional unit test failure) [Luis Alejandro Martínez Faneyth]

* Chore: retrigger PR CI after #657 merge. [Luis Alejandro Martínez Faneyth]

* Fix(ci): mark workspace safe for git in Semgrep container. [Cursor Agent]

* Fix(ci): run PR workflows on feature branch push. [Luis Alejandro Martínez Faneyth]

* Test: remove CI auto-merge probe v3 (fix intentional failure) [Cursor Agent]

* Test: re-break probe v3 for Cursor fix → auto-merge validation. [Luis Alejandro Martínez Faneyth]

* Test: remove CI auto-merge probe v3 (fix intentional failure) [Cursor Agent]

* Test: CI auto-merge probe v3 (intentional unit test failure) [Luis Alejandro Martínez Faneyth]

* Chore: retrigger PR CI after probe fix. [Luis Alejandro Martínez Faneyth]

* Test: remove CI auto-merge probe v2 (fix intentional failure) [Luis Alejandro Martínez Faneyth]

* Test: CI auto-merge probe v2 (cleanup + failing unit test) [Luis Alejandro Martínez Faneyth]

* Add .cursorrules with Cursor Cloud dev environment instructions. [Cursor Agent]

* Test: make lint probe fail flake8 F841. [Luis Alejandro Martínez Faneyth]

* Test: intentional lint failure for CI auto-merge probe. [Luis Alejandro Martínez Faneyth]

* Docs: verify Semgrep fleet migration. [Luis Alejandro Martínez Faneyth]

* Chore: sync PR auto-merge, CodeQL PR gate, and maintainer files from rosey-maintain. [Luis Alejandro Martínez Faneyth]

* Fixing tests. [Luis Alejandro Martínez Faneyth]

* Improving maintainer files. [Luis Alejandro Martínez Faneyth]

* Chore: fleet release parity — gates, dependabot, hotfix removal. [Luis Alejandro Martínez Faneyth]

* Improving release documentation and maintainer scripts. [Luis Alejandro Martínez Faneyth]


2.0.1 (2026-06-15)
------------

Other
~~~~~~~~~~~~

* Updating documentation. [Luis Alejandro Martínez Faneyth]


2.0.0 (2026-06-15)
------------

Other
~~~~~~~~~~~~

* Fixing release scripts. [Luis Alejandro Martínez Faneyth]

* Preparing release. [Luis Alejandro Martínez Faneyth]

* Improving test scripts. [Luis Alejandro Martínez Faneyth]

* Apply rosey maintainer fleet sync. [Luis Alejandro Martínez Faneyth]

* Apply rosey maintainer fleet sync. [Luis Alejandro Martínez Faneyth]

* Improving. [Luis Alejandro Martínez Faneyth]

* Improving e2e tests. [Luis Alejandro Martínez Faneyth]

* Improving architecture. [Luis Alejandro Martínez Faneyth]

* Improving e2e tests. [Luis Alejandro Martínez Faneyth]

* Fixing tiktok error recognition. [Luis Alejandro Martínez Faneyth]


1.1.6 (2026-01-25)
------------

Added
~~~~~~~~~~~~

* Adding future plans. [Luis Alejandro Martínez Faneyth]

* Starting the threads implementation plan (Phase 1) [Luis Alejandro Martínez Faneyth]


Changed
~~~~~~~~~~~~

* Improving architechture consistency and planning next features. [Luis Alejandro Martínez Faneyth]

* Implementing object-oriented programming. [Luis Alejandro Martínez Faneyth]

* Adding tiktok, discord and youtube social networks. [Luis Alejandro Martínez Faneyth]


Fixed
~~~~~~~~~~~~

* Fixing pipeline. [Luis Alejandro Martínez Faneyth]

* Fixing readthedocs building. [Luis Alejandro Martínez Faneyth]

* Fixing problem with coveralls action. [Luis Alejandro Martínez Faneyth]


Other
~~~~~~~~~~~~

* Preparing version for bumpversion. [Luis Alejandro Martínez Faneyth]

* Adding setup.py top level file to be able to install it via pip as monorepo. [Luis Alejandro Martínez Faneyth]

* Fixing tests. [Luis Alejandro Martínez Faneyth]

* Fixing tests. [Luis Alejandro Martínez Faneyth]

* Improving documentation on tiktok. [Luis Alejandro Martínez Faneyth]

* Setting default credentials. [Luis Alejandro Martínez Faneyth]

* Increasing coverage. [Luis Alejandro Martínez Faneyth]

* Fixing tests. [Luis Alejandro Martínez Faneyth]

* Fixinf lint errors. [Luis Alejandro Martínez Faneyth]

* Fixing several usage bugs. [Luis Alejandro Martínez Faneyth]

* Adding support to python 3.13 and 3.14. Removing Python 3.9. [Luis Alejandro Martínez Faneyth]

* Update requirements-dev.txt. [Luis Alejandro]

* Update requirements-dev.txt. [Luis Alejandro]

* Fixing more dependency conflicts. [Luis Alejandro Martínez Faneyth]

* Fixing dependency conflict. [Luis Alejandro Martínez Faneyth]

* Fixing dependency conflict. [Luis Alejandro Martínez Faneyth]

* Fixing jinja2 version. [Luis Alejandro Martínez Faneyth]

* Adding RTD building and trigger. [Luis Alejandro Martínez Faneyth]

* Fixing coverage report. [Luis Alejandro Martínez Faneyth]

* Fixing lint errors. [Luis Alejandro Martínez Faneyth]

* Improving test coverage and updating documentation. [Luis Alejandro Martínez Faneyth]

* Final cleanup: Remove migration working docs (Week 3.5 Day 6) [Luis Alejandro Martínez Faneyth]

* Update documentation for v2.0 modular package structure (Week 3.5 Day 5) [Luis Alejandro Martínez Faneyth]

* Update integration test scripts for v2.0 CLI structure (Week 3.5 Day 4) [Luis Alejandro Martínez Faneyth]

* Update root configuration for modular package structure (Week 3.5 Day 3) [Luis Alejandro Martínez Faneyth]

* Remove old monolithic codebase (Week 3.5 Day 2) [Luis Alejandro Martínez Faneyth]

* Refactoring command line interface. [Luis Alejandro Martínez Faneyth]

* Update keepalive.yml. [Luis Alejandro]


1.1.5 (2026-01-20)
------------

Other
~~~~~~~~~~~~

* Adding readthedocs requirements. [Luis Alejandro Martínez Faneyth]


1.1.4 (2026-01-19)
------------

Other
~~~~~~~~~~~~

* Adding readthedocs configuration. [Luis Alejandro Martínez Faneyth]


1.1.3 (2023-09-05)
------------

Changed
~~~~~~~~~~~~

* Adding support for link embed in facebook and linkedin. [Luis Alejandro Martínez Faneyth]


1.1.2 (2023-09-03)
------------

Changed
~~~~~~~~~~~~

* Improving documentation. [Luis Alejandro Martínez Faneyth]


1.1.1 (2023-09-01)
------------

Changed
~~~~~~~~~~~~

* Improving versioning workflow. [Luis Alejandro Martínez Faneyth]

* Improving pipeline. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Adding placeholder for github actions documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]


Fixed
~~~~~~~~~~~~

* Fixing functional tests. [Luis Alejandro Martínez Faneyth]


1.1.0 (2023-08-31)
------------

Changed
~~~~~~~~~~~~

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Rewriting linkedin module to use official api. [Luis Alejandro Martínez Faneyth]


Other
~~~~~~~~~~~~

* Test. [Luis Alejandro Martínez Faneyth]


1.0.1 (2023-08-30)
------------

Changed
~~~~~~~~~~~~

* Improving linkedin authentication. [Luis Alejandro Martínez Faneyth]

* Fixing test. [Luis Alejandro Martínez Faneyth]


1.0.0 (2023-08-29)
------------

Changed
~~~~~~~~~~~~

* Updating version. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Removing support for python 3.8. [Luis Alejandro Martínez Faneyth]

* Improving reliability of scripts. [Luis Alejandro Martínez Faneyth]

* Downgrading coverage because coveralls doesnt support version 7 yet. [Luis Alejandro Martínez Faneyth]

* Adding functiona; tests. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Completing LinkedIn functionality. Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Improving documentation. [Luis Alejandro Martínez Faneyth]

* Fixing PR workflow. [Luis Alejandro Martínez Faneyth]

* Developing functions. [Luis Alejandro Martínez Faneyth]

* Changing name to Agora. [Luis Alejandro Martínez Faneyth]

* Developing Instagram and LinkedIn actions. [Luis Alejandro Martínez Faneyth]

* Adding basic functionalities. [Luis Alejandro Martínez Faneyth]


Fixed
~~~~~~~~~~~~

* Allowing python 3.11 build to fail without failing entire workflow, also on PRs. [Luis Alejandro Martínez Faneyth]

* Allowing python 3.11 build to fail without failing entire workflow. [Luis Alejandro Martínez Faneyth]


Other
~~~~~~~~~~~~

* Update requirements.txt. [Luis Alejandro]

* Initial commit. [Luis Alejandro Martínez Faneyth]

