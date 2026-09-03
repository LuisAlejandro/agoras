---
title: "U1 Guard-composition audit: platform api method inventory"
type: audit
date: 2026-09-02
plan: rosey/plans/2026-09-02-001-refactor-platform-api-guard-decorator-plan.md
status: complete
---

# U1 Guard-Composition Audit — Authoritative Per-Method Baseline

Branch: `feature/platform-api-guard-decorator`. All ten modules read in full on 2026-09-02;
counts below are fresh AST/grep derivations, not the 176/194 figures taken on faith.

## Guard-sequence legend (letters a–h)

| Code | Guard |
|---|---|
| a | Auto-auth: `if not self._authenticated: await self.authenticate()` |
| b | Assert: `if not self._authenticated or not self.client: raise` |
| c | Auth-manager ensure: `self.auth_manager.ensure_authenticated()` |
| d | Token-presence: `if not self.access_token: raise` |
| e | Client-presence: `if not self.client: raise` |
| e* | Client-presence **compound** (linkedin): `if not self.client or not self.object_id: raise` |
| e-inner | Client-presence **re-check inside the `to_thread` closure** (tiktok, threads) |
| f | Rate limit: `await self._rate_limit_check("<literal-bucket>", <interval>)` |
| g | Error wrap: `try/except` → `self._handle_api_error(e, "<op label>")` + re-raise |
| h | None — not-supported raise or guard-less delegation |

Conventions: `authenticate`/`disconnect` are the auth lifecycle, not guarded operations.
`_handle_api_error` raises `Exception("<op label> failed: <sanitized>") from error`
(core `api_base.py:115-116`; sanitizer covers 3 patterns at `api_base.py:91-95`).
`raise_authentication_error_from_manager(self.auth_manager)` appears exactly once per
platform (10 call sites) inside `authenticate`.

---

## Per-Platform Method Inventory

### x — dialect: **assert-or-raise (b)**

| Method | Sequence | Message template | Rate limit | Error wrap |
|---|---|---|---|---|
| `authenticate` | — (auth lifecycle) | `raise_authentication_error_from_manager` | — | — |
| `disconnect` | — (hook: `client.disconnect()` yes) | — | — | — |
| `upload_media` | b f g | `"X API not authenticated"` | `("upload_media", 1.0)` | `"X media upload"` |
| `post` | b f (logic) g | `"X API not authenticated"` | `("post", 1.0)` | `"X tweet creation"` |
| `like` | b f g | `"X API not authenticated"` | `("like", 0.5)` | `"X like"` |
| `reply` | b f g | `"X API not authenticated"` | `("post", 1.0)` — **shares post bucket** | `"X reply creation"` |
| `share` | b f g | `"X API not authenticated"` | `("share", 0.5)` | `"X retweet"` |
| `delete` | b f g | `"X API not authenticated"` | `("delete", 0.5)` | `"X delete"` |
| `get_post` | b f g | `"X API not authenticated"` | `("get_post", 0.5)` | `"X get-post"` |
| `list_posts` | b f (logic) g | `"X API not authenticated"`; also `"Unable to resolve X user id for list-posts."` (inside try) | `("list_posts", 0.5)` | `"X list-posts"` |
| `_subscription_type` | — (private helper) | — | — | — |

Exact not-supported: none. `post` also runs `validate_text("twitter", ...)` between f and g
when `validate=True`; `list_posts` resolves user id between f and the client call, inside the try.

### discord — dialect: **auto-auth (a)**

| Method | Sequence | Message template | Rate limit | Error wrap |
|---|---|---|---|---|
| `authenticate` | — | `"Discord client not available after authentication"`; `raise_authentication_error_from_manager` | — | — |
| `disconnect` | — (hook: `client.disconnect()` yes) | — | — | — |
| `post` | a e f | `"Discord client not available"` | `("post", 1.0)` | — |
| `reply` | a e f | `"Discord client not available"` | `("reply", 1.0)` | — |
| `create_public_thread` | a e f | `"Discord client not available"` | `("create_public_thread", 1.0)` | — |
| `send_message_to_thread` | a e f | `"Discord client not available"` | `("send_message_to_thread", 1.0)` | — |
| `like` | a e f | `"Discord client not available"` | `("like", 0.5)` | — |
| `delete` | a e f | `"Discord client not available"` | `("delete", 0.5)` | — |
| `get_post` | a e f g | `"Discord client not available"` | `("get_post", 0.5)` | `"Discord get-post"` |
| `list_posts` | a e f g | `"Discord client not available"` | `("list_posts", 0.5)` | `"Discord list-posts"` |
| `upload_file` | a e f | `"Discord client not available"` | `("upload_file", 1.0)` | — |
| `share` | **h** | `"Share not supported for Discord"` | — | — |
| `create_embed` | **e** (sync, client-check-only) | `"Discord client not available"` | — | — |

Exceptions to dominant shape: `get_post`/`list_posts` carry the only two error wraps;
`share` is not-supported; `create_embed` is a **sync** client-check-only method (no auth
attempt, no rate limit, no wrap).

### telegram — dialect: **auto-auth (a)**

| Method | Sequence | Message template | Rate limit | Error wrap |
|---|---|---|---|---|
| `authenticate` | — | `"Telegram client not available after authentication"`; `raise_authentication_error_from_manager` | — | — |
| `disconnect` | — (hook: **no** `client.disconnect()`; clears `auth_manager.client`) | — | — | — |
| `get_bot_info` | a e g | `"Telegram client not available"` | — | `"Telegram get bot info"` |
| `send_message` | a e f g | `"Telegram client not available"` | `("send_message", 1.0)` | `"Telegram send message"` |
| `send_photo` | a e f (media logic) g | `"Telegram client not available"`; `"No photo content available"`; `"Failed to download image"`; `f"Failed to validate image: {image.url}"` | `("send_photo", 1.0)` | `"Telegram send photo"` |
| `send_video` | a e f (media logic) g | `"Telegram client not available"`; `"No video content available"`; `f"Failed to validate video: {video.url}"` | `("send_video", 1.0)` | `"Telegram send video"` |
| `delete_message` | a e f g | `"Telegram client not available"` | `("delete_message", 0.5)` | `"Telegram delete message"` |
| `post` | **h** (validation + delegate to `send_message`) | `"Telegram chat_id is required for posting"`; `"Telegram text is required for posting"` | — (via delegate) | — (via delegate) |
| `delete` | **h** (validation + delegate to `delete_message`) | `"Telegram chat_id is required for deletion"`; `f"Invalid message ID: {post_id}"` | — (via delegate) | — (via delegate) |
| `share` | **h** | `"Share not supported for Telegram"` | — | — |
| `like` | **h** | `"Like not supported for Telegram"` | — | — |
| `send_media_group` | a e f g | `"Telegram client not available"` | `("send_media_group", 1.0)` | `"Telegram send media group"` |
| `reply` | a e (media dispatch) | `"Telegram client not available"`; `"Telegram chat_id is required for reply"` | — (via delegates) | — (via delegates) |

Exceptions: `get_bot_info` has **no rate limit**; `reply` has no rate limit/wrap of its own
but its delegates (`send_media_group`/`send_photo`/`send_video`/`send_message`) re-run the
full a+e+f+g stack — the **double-wrap hazard** for U4; `post`/`delete` are guard-less
validation+delegation; `like`/`share` not-supported.

### facebook — dialect: **auth-manager ensure (c)** — highest wrap density (15)

| Method | Sequence | Message template | Rate limit | Error wrap |
|---|---|---|---|---|
| `authenticate` | — | `raise_authentication_error_from_manager` | — | — |
| `disconnect` | — (hook: `client.disconnect()` yes) | — | — | — |
| `check_if_page` | c e f g | `"Facebook API not authenticated"` | `("check_if_page", 0.1)` | `"Facebook page check"` |
| `get_page_token` | c e f (inner token) g | `"Facebook API not authenticated"`; `"Facebook access token not available"` (inside try) | `("get_page_token", 0.5)` | `"Facebook page token exchange"` |
| `post` | c e f g | `"Facebook API not authenticated"` | `("post", 1.0)` | `"Facebook post creation"` |
| `upload_media` | c e f g | `"Facebook API not authenticated"` | `("upload_media", 1.0)` | `"Facebook media upload"` |
| `upload_photo_file` | c e f g | `"Facebook API not authenticated"` | `("upload_photo_file", 1.0)` | `"Facebook photo file upload"` |
| `like` | c e f g | `"Facebook API not authenticated"` | `("like", 0.5)` | `"Facebook like"` |
| `reply` | c e f g | `"Facebook API not authenticated"` | `("reply", 0.5)` | `"Facebook comment"` |
| `delete` | c e f g | `"Facebook API not authenticated"` | `("delete", 0.5)` | `"Facebook delete"` |
| `delete_reply` | c e f g | `"Facebook API not authenticated"` | `("delete", 0.5)` — **shares delete bucket** | `"Facebook delete-reply"` |
| `get_post` | c e f g | `"Facebook API not authenticated"` | `("get_post", 0.5)` | `"Facebook get-post"` |
| `get_reply` | c e f g | `"Facebook API not authenticated"` | `("get_reply", 0.5)` | `"Facebook get-reply"` |
| `list_posts` | c e f g | `"Facebook API not authenticated"` | `("list_posts", 0.5)` | `"Facebook list-posts"` |
| `share` | c e f g | `"Facebook API not authenticated"` | `("share", 1.0)` | `"Facebook share"` |
| `upload_reel_or_story` | c e f g | `"Facebook API not authenticated"` | `("upload_reel_or_story", 1.0)` | `"Facebook reel or story upload"` |
| `upload_regular_video` | c e f (app-id check) g | `"Facebook API not authenticated"`; `"Facebook app ID is required for regular video uploads"` (between f and g) | `("upload_regular_video", 1.0)` | `"Facebook regular video upload"` |

No per-method guard-shape exceptions; uniform c e f g on all 13 operations.

### instagram — dialect: **auth-manager ensure (c)**

| Method | Sequence | Message template | Rate limit | Error wrap |
|---|---|---|---|---|
| `authenticate` | — | `raise_authentication_error_from_manager` | — | — |
| `disconnect` | — (hook: `client.disconnect()` yes) | — | — | — |
| `post` | c e f g | `"Instagram API not authenticated"` | `("post", 1.0)` | `"Instagram post creation"` |
| `create_media` | c e f g | `"Instagram API not authenticated"` | `("create_media", 1.0)` | `"Instagram media creation"` |
| `create_resumable_video` | c e f g | `"Instagram API not authenticated"` | `("create_resumable_video", 1.0)` | `"Instagram resumable video upload"` |
| `create_carousel` | **e** f g | `"Instagram API not authenticated"` | `("create_carousel", 1.0)` | `"Instagram carousel creation"` |
| `publish_media` | **e** f g | `"Instagram API not authenticated"` | `("publish_media", 1.0)` | `"Instagram media publishing"` |
| `like` | **h** | `"Like not supported for Instagram"` | — | — |
| `delete` | c e f g | `"Instagram API not authenticated"` | `("delete", 0.5)` | `"Instagram delete"` |
| `share` | **h** | `"Share not supported for Instagram"` | — | — |
| `reply` | c e f g | `"Instagram API not authenticated"` | `("reply", 0.5)` | `"Instagram comment"` |
| `delete_reply` | c e f g | `"Instagram API not authenticated"` | `("delete", 0.5)` — **shares delete bucket** | `"Instagram delete-reply"` |
| `get_post` | c e f g | `"Instagram API not authenticated"` | `("get_post", 0.5)` | `"Instagram get-post"` |
| `get_reply` | c e f g | `"Instagram API not authenticated"` | `("get_reply", 0.5)` | `"Instagram get-reply"` |
| `list_posts` | c e f g | `"Instagram API not authenticated"` | `("list_posts", 0.5)` | `"Instagram list-posts"` |

Exceptions: `create_carousel` and `publish_media` are **client-check-only** (no ensure).

### linkedin — dialect: **auth-manager ensure (c)**; compound e*

| Method | Sequence | Message template | Rate limit | Error wrap |
|---|---|---|---|---|
| `authenticate` | — | `raise_authentication_error_from_manager` | — | — |
| `disconnect` | — (hook: `client.disconnect()` yes) | — | — | — |
| `upload_video` | c e* f g | `"LinkedIn API not authenticated"` | `("upload_video", 2.0)` | `"LinkedIn video upload"` |
| `upload_image` | c e* f g | `"LinkedIn API not authenticated"` | `("upload_image", 1.0)` | `"LinkedIn image upload"` |
| `post` | c e f g | `"LinkedIn API not authenticated"` | `("post", 1.0)` | `"LinkedIn post creation"` |
| `like` | **e\*** f g | `"LinkedIn API not authenticated"` | `("like", 0.5)` | `"LinkedIn like"` |
| `reply` | **e\*** f g | `"LinkedIn API not authenticated"` | `("reply", 0.5)` | `"LinkedIn comment"` |
| `share` | **e** f g | `"LinkedIn API not authenticated"` | `("share_post", 1.0)` | `"LinkedIn share"` |
| `delete` | **e** f g | `"LinkedIn API not authenticated"` | `("delete", 0.5)` | `"LinkedIn delete"` |
| `delete_reply` | **e** f g | `"LinkedIn API not authenticated"` | `("delete", 0.5)` — **shares delete bucket** | `"LinkedIn delete-reply"` |
| `get_post` | c e f g | `"LinkedIn API not authenticated"` | `("get_post", 0.5)` | `"LinkedIn get-post"` |
| `get_reply` | c e f g | `"LinkedIn API not authenticated"` | `("get_reply", 0.5)` | `"LinkedIn get-reply"` |
| `get_media` | c e f g | `"LinkedIn API not authenticated"` | `("get_media", 0.5)` | `"LinkedIn get-media"` |
| `list_posts` | c e* f g | `"LinkedIn API not authenticated"` | `("list_posts", 0.5)` | `"LinkedIn list-posts"` |

Exceptions: **five** client-check-only methods — `like`, `reply` (e*), `share`, `delete`,
`delete_reply` (e). `upload_video`/`upload_image`/`list_posts` use the compound e*
(`client or object_id`). `post` reads `self.object_id` in the client call with no presence
guard (may be `None` at call time — today's behavior, preserved).

### threads — dialect: **auth-manager ensure (c)**; token+d (d) on most

| Method | Sequence | Message template | Rate limit | Error wrap |
|---|---|---|---|---|
| `authenticate` | — | `raise_authentication_error_from_manager` | — | — |
| `disconnect` | — (hook: **no** `client.disconnect()`) | — | — | — |
| `get_profile` | **d** e-inner g | `"Threads API not authenticated"`; `"Threads client not available"` (inner) | — | `"Threads get profile"` |
| `create_post` | c d e f (media logic) g | `"Threads API not authenticated"`; `"Threads client not available"`; `"File captions count ({n}) must match files count ({n})"`; local-upload rejection (2-line template); `f"Failed to download or validate image: {image.url}"` | `("create_post", 2.0)` | `"Threads post creation"` |
| `create_video_post` | c d e (url checks) f g | `"Threads API not authenticated"`; `"Threads client not available"`; `"Video URL is required"`; local-upload rejection; `f"Failed to download or validate video: {video.url}"` | `("create_video_post", 2.0)` | `"Threads video post creation"` |
| `repost_post` | c d e f g | `"Threads API not authenticated"`; `"Threads client not available"` | `("repost_post", 2.0)` | `"Threads repost"` |
| `post` | **h** (pure delegate to `create_post`) | — | — (via delegate) | — (via delegate) |
| `like` | **h** | `"Like not supported for Threads"` | — | — |
| `delete` | c d e (id check) f g | `"Threads API not authenticated"`; `"Threads client not available"`; `"Post ID is required for delete action."` | `("delete_post", 1.0)` | `"Threads post deletion"` |
| `get_post` | c d e (id check) f g | `"Threads API not authenticated"`; `"Threads client not available"`; `"Post ID is required for get-post action."` | `("get_post", 1.0)` | `"Threads get-post"` |
| `list_posts` | c d e f g | `"Threads API not authenticated"`; `"Threads client not available"` | `("list_posts", 1.0)` | `"Threads list-posts"` |
| `share` | **h** (pure delegate to `repost_post`) | — | — (via delegate) | — (via delegate) |

Exceptions: `get_profile` is **token-presence-only** (d, no ensure, no rate limit) with the
client check nested inside the closure; `post`/`share` pure delegation; `like` not-supported.
All client checks appear both top-level and re-checked inside `to_thread` closures (e-inner).

### tiktok — dialect: **auth-manager ensure (c)**; pilot (lowest density)

| Method | Sequence | Message template | Rate limit | Error wrap |
|---|---|---|---|---|
| `authenticate` | — | `raise_authentication_error_from_manager` (no post-auth client check — unlike discord/telegram) | — | — |
| `disconnect` | — (hook: **no** `client.disconnect()`; clears `auth_manager.client`) | — | — | — |
| `get_creator_info` | **h** (pure delegate to `refresh_creator_info`) | — | — (via delegate) | — (via delegate) |
| `refresh_creator_info` | c d e e-inner (logic) g-conditional | `"TikTok API not authenticated"`; `"TikTok client not available"`; `f"Username mismatch: {username} != {expected}"`; `"TikTok says this creator cannot post right now. Try again later."` | — | `"TikTok get creator info"` — **selective**: re-raises unmodified if message contains `"Username mismatch"` or `"not authenticated"`, else wraps |
| `upload_video` | c d e e-inner f g | `"TikTok API not authenticated"`; `"TikTok client not available"` | `("upload_video", 2.0)` | `"TikTok video upload"` |
| `upload_video_file` | c d e e-inner f g | `"TikTok API not authenticated"`; `"TikTok client not available"` | `("upload_video_file", 2.0)` | `"TikTok video file upload"` |
| `upload_photo` | c d e e-inner f g | `"TikTok API not authenticated"`; `"TikTok client not available"` | `("upload_photo", 2.0)` | `"TikTok photo upload"` |
| `_wait_for_publish_completion` | e-inner (loop) g | `"TikTok client not available"` (inner); `f"Publish timeout after {max_wait_time} seconds"` | — | `"TikTok status check"` |
| `post` | **h** | `"Regular posts not supported for TikTok - use upload_photo() method instead"` | — | — |
| `like` | **h** | `"Like not supported for TikTok"` | — | — |
| `delete` | **h** | `"Delete not supported for TikTok"` | — | — |
| `share` | **h** | `"Share not supported for TikTok"` | — | — |

Carries **two** guard templates (`"TikTok API not authenticated"`, `"TikTok client not available"`).
3 rate-limit sites, 5 error-wrap sites — the U3 pilot baseline.

### whatsapp — dialect: **auth-manager ensure (c)** — most uniform

| Method | Sequence | Message template | Rate limit | Error wrap |
|---|---|---|---|---|
| `authenticate` | — | `raise_authentication_error_from_manager` | — | — |
| `disconnect` | — (hook: `client.disconnect()` yes) | — | — | — |
| `post` | c e f (media dispatch) g | `"WhatsApp API not authenticated"`; `"No text, image, or video provided for WhatsApp message"`; `f"Failed to validate video: {video.url}"`; `f"Failed to validate image: {image_url}"` | `("post", 1.0)` | `"WhatsApp post creation"` (wraps entire dispatch incl. delegates) |
| `send_message` | c e f g | `"WhatsApp API not authenticated"` | `("send_message", 1.0)` | `"WhatsApp send_message"` |
| `upload_media` | c e f g | `"WhatsApp API not authenticated"` | `("upload_media", 1.0)` | `"WhatsApp upload_media"` |
| `send_image` | c e f g | `"WhatsApp API not authenticated"` | `("send_image", 1.0)` | `"WhatsApp send_image"` |
| `send_video` | c e f g | `"WhatsApp API not authenticated"` | `("send_video", 1.0)` | `"WhatsApp send_video"` |
| `reply` | **h** (pure delegate to send_image/send_video/send_message) | — | — (via delegates) | — (via delegates) |
| `get_business_profile` | c e f g | `"WhatsApp API not authenticated"`; `f"Failed to get business profile: {response}"` (inside closure) | `("get_business_profile", 1.0)` | `"WhatsApp get_business_profile"` |
| `like` | **h** | `"Like not supported for WhatsApp"` | — | — |
| `delete` | **h** | `"Delete not supported for WhatsApp"` | — | — |
| `share` | **h** | `"Share not supported for WhatsApp"` | — | — |
| `send_template` | c e (name check) f g | `"WhatsApp API not authenticated"`; `"Template name is required."` (between e and f) | `("send_template", 1.0)` | `"WhatsApp send_template"` |

One guard template (`"WhatsApp API not authenticated"`). `post` dispatch re-enters the
send_* methods (guards re-run — wrap scope covers the whole body).

### youtube — dialect: **auth-manager ensure (c)**

| Method | Sequence | Message template | Rate limit | Error wrap |
|---|---|---|---|---|
| `authorize` | — (OAuth flow, not guarded) | `"YouTube authorization failed"` | — | — |
| `authenticate` | — | `raise_authentication_error_from_manager` | — | — |
| `disconnect` | — (hook: `client.disconnect()` yes) | — | — | — |
| `upload_video` | c e f g | `"YouTube API not authenticated"` | `("upload_video", 2.0)` | `"YouTube video upload"` |
| `like` | c e f g | `"YouTube API not authenticated"` | `("like", 1.0)` | `"YouTube video like"` |
| `delete` | **e** f g | `"YouTube API not authenticated"` | `("delete", 1.0)` | `"YouTube video deletion"` |
| `post` | **h** | `"Regular posts not supported for YouTube - use upload_video() method instead"` | — | — |
| `share` | **h** | `"Share not supported for YouTube"` | — | — |
| `reply` | c e f g | `"YouTube API not authenticated"` | `("reply", 1.0)` | `"YouTube comment"` |
| `delete_reply` | c e f g | `"YouTube API not authenticated"` | `("delete", 1.0)` — **shares delete bucket** | `"YouTube delete-reply"` |
| `get_post` | c e f g | `"YouTube API not authenticated"` | `("get_post", 1.0)` | `"YouTube get-post"` |
| `get_reply` | c e f g | `"YouTube API not authenticated"` | `("get_reply", 1.0)` | `"YouTube get-reply"` |
| `list_posts` | c e f g | `"YouTube API not authenticated"` | `("list_posts", 1.0)` | `"YouTube list-posts"` |

Exception: `delete` is **client-check-only** (no ensure).

---

## Consolidated Section

### Dialect per platform

| Dialect | Platforms | Discriminating signal |
|---|---|---|
| Auto-authenticate (a) | discord, telegram | `if not self._authenticated: await self.authenticate()` then client check |
| Assert-or-raise (b) | x | `if not self._authenticated or not self.client: raise` |
| Auth-manager ensure (c) | facebook, instagram, linkedin, threads, tiktok, whatsapp, youtube | `self.auth_manager.ensure_authenticated()` (55 sites), then e and — tiktok/threads only — d |
| Client-check only (e) | per-method exceptions | discord `create_embed`; instagram `create_carousel`/`publish_media`; linkedin `like`/`reply`/`share`/`delete`/`delete_reply`; youtube `delete` |

### Method counts (fresh AST, class-level defs)

| Platform | Plain | Property | Staticmethod | Total | Inline nested `def`s | All `def` lines |
|---|---|---|---|---|---|---|
| x | 12 | 6 | 0 | 18 | 0 | 18 |
| discord | 14 | 4 | 0 | 18 | 0 | 18 |
| telegram | 14 | 2 | 0 | 16 | 0 | 16 |
| facebook | 18 | 0 | 0 | 18 | 0 | 18 |
| instagram | 16 | 2 | 0 | 18 | 0 | 18 |
| linkedin | 15 | 7 | 0 | 22 | 0 | 22 |
| threads | 14 | 3 | 2 | 19 | 7 | 26 |
| tiktok | 13 | 2 | 0 | 15 | 5 | 20 |
| whatsapp | 14 | 0 | 0 | 14 | 6 | 20 |
| youtube | 14 | 4 | 0 | 18 | 0 | 18 |
| **Total** | **144** | **30** | **2** | **176** | **18** | **194** |

- **176** = total class-level defs (the "176 public methods" figure; includes 30
  properties + 2 staticmethods — none carry guards).
- **194** = all `def` lines including the 18 inline `to_thread` closures (tiktok 5,
  threads 7, whatsapp 6) — the plan's "modules contain 194" figure.
- Guarded-operation denominators (methods with a non-h sequence): x 8, discord 10
  (excl. `create_embed` 1, `share` 1), telegram 6, facebook 13, instagram 11, linkedin 12,
  threads 7, tiktok 4, whatsapp 7, youtube 7.

### Not-supported / no-guard inventory (h) — 15 not-supported + 6 delegation

Not-supported (raise-only, no guard/rate-limit/wrap runs before the raise):

| Platform | Methods | Exact messages |
|---|---|---|
| tiktok | `post`, `like`, `delete`, `share` | `"Regular posts not supported for TikTok - use upload_photo() method instead"` / `"Like not supported for TikTok"` / `"Delete not supported for TikTok"` / `"Share not supported for TikTok"` |
| discord | `share` | `"Share not supported for Discord"` |
| telegram | `like`, `share` | `"Like not supported for Telegram"` / `"Share not supported for Telegram"` |
| instagram | `like`, `share` | `"Like not supported for Instagram"` / `"Share not supported for Instagram"` |
| threads | `like` | `"Like not supported for Threads"` |
| whatsapp | `like`, `delete`, `share` | `"Like not supported for WhatsApp"` / `"Delete not supported for WhatsApp"` / `"Share not supported for WhatsApp"` |
| youtube | `post`, `share` | `"Regular posts not supported for YouTube - use upload_video() method instead"` / `"Share not supported for YouTube"` |

Guard-less delegation (h, no direct guards; guards/rate-limit/wrap run via the delegate):

| Platform | Methods | Delegates to |
|---|---|---|
| tiktok | `get_creator_info` | `refresh_creator_info` |
| telegram | `post`, `delete` | `send_message`, `delete_message` (validation raises precede delegation) |
| threads | `post`, `share` | `create_post`, `repost_post` |
| whatsapp | `reply` | `send_image`/`send_video`/`send_message` |

### Disconnect-hook inventory

Calls `client.disconnect()` in `disconnect()`: **x, discord, facebook, instagram, linkedin,
whatsapp, youtube** (7). Does **not**: **tiktok, telegram, threads** (3) — they clear
`auth_manager.client`/`user_info` instead. Note threads' `disconnect` does not even clear
`auth_manager.access_token` (clears only base client + flag).

### Guard-phase message templates (per platform, guard-relevant)

| Platform | Templates |
|---|---|
| x | `"X API not authenticated"` |
| discord | `"Discord client not available"` (+ `"Discord client not available after authentication"` in `authenticate`) |
| telegram | `"Telegram client not available"` (+ `"Telegram client not available after authentication"` in `authenticate`) |
| facebook | `"Facebook API not authenticated"` |
| instagram | `"Instagram API not authenticated"` |
| linkedin | `"LinkedIn API not authenticated"` |
| threads | **two**: `"Threads API not authenticated"`, `"Threads client not available"` |
| tiktok | **two**: `"TikTok API not authenticated"`, `"TikTok client not available"` |
| whatsapp | `"WhatsApp API not authenticated"` |
| youtube | `"YouTube API not authenticated"` |

Guard-phase raise sites are bare `raise Exception(<template>)` with no chained cause
(`__cause__ is None`); only `_handle_api_error` (g) chains (`raise ... from error`).

### Rate-limit bucket inventory (all 84 sites; literal key, interval, platforms)

| Bucket key | Interval | Platforms |
|---|---|---|
| `check_if_page` | 0.1 | facebook |
| `upload_media` | 1.0 | x, facebook, whatsapp |
| `post` | 1.0 | x, discord, facebook, instagram, linkedin, whatsapp |
| `reply` | 1.0 | discord, facebook, linkedin, youtube (x: shares `post` bucket) |
| `reply` | 0.5 | x, instagram |
| `like` | 0.5 | x, discord, facebook, instagram, linkedin |
| `like` | 1.0 | youtube |
| `share` | 0.5 | x |
| `share` | 1.0 | facebook |
| `share_post` | 1.0 | linkedin (share) |
| `delete` | 0.5 | x, discord, facebook, instagram, linkedin |
| `delete` | 1.0 | youtube (delete **and** delete_reply share) |
| `get_post` | 0.5 | x, discord, facebook, instagram, linkedin |
| `get_post` | 1.0 | threads, youtube |
| `list_posts` | 0.5 | x, discord, facebook, instagram, linkedin |
| `list_posts` | 1.0 | threads, youtube |
| `upload_file` | 1.0 | discord |
| `create_public_thread` | 1.0 | discord |
| `send_message_to_thread` | 1.0 | discord |
| `get_page_token` | 0.5 | facebook |
| `get_reply` | 0.5 | facebook, instagram, linkedin |
| `get_reply` | 1.0 | youtube |
| `get_media` | 0.5 | linkedin |
| `upload_reel_or_story` | 1.0 | facebook |
| `upload_regular_video` | 1.0 | facebook |
| `upload_photo_file` | 1.0 | facebook |
| `upload_video` | 2.0 | tiktok, linkedin, youtube |
| `upload_video_file` | 2.0 | tiktok |
| `upload_photo` | 2.0 | tiktok |
| `upload_image` | 1.0 | linkedin |
| `create_media` | 1.0 | instagram |
| `create_resumable_video` | 1.0 | instagram |
| `create_carousel` | 1.0 | instagram |
| `publish_media` | 1.0 | instagram |
| `send_message` | 1.0 | telegram, whatsapp |
| `send_photo` | 1.0 | telegram |
| `send_video` | 1.0 | telegram, whatsapp |
| `send_media_group` | 1.0 | telegram |
| `delete_message` | 0.5 | telegram |
| `send_image` | 1.0 | whatsapp |
| `get_business_profile` | 1.0 | whatsapp |
| `send_template` | 1.0 | whatsapp |
| `create_post` | 2.0 | threads |
| `create_video_post` | 2.0 | threads |
| `repost_post` | 2.0 | threads |
| `delete_post` | 1.0 | threads (delete) |
| `upload_video` | 2.0 | youtube |

Shared buckets across methods on one platform: x `reply`→`post`; facebook
`delete_reply`→`delete`; instagram `delete_reply`→`delete`; linkedin
`delete_reply`→`delete`; youtube `delete_reply`→`delete`.

---

## Reconciliation vs Known Figures

| Figure | Expected | Measured | Status |
|---|---|---|---|
| Method denominator (all `def` lines incl. nested) | 194 | 194 (176 class-level + 18 nested closures) | ✅ |
| Public method count | 176 | 176 class-level defs (144 plain + 30 properties + 2 staticmethods) | ✅ |
| Rate-limit sites (`await self._rate_limit_check`) | 84 | 84 (x 8, discord 9, telegram 5, facebook 15, instagram 11, linkedin 12, threads 6, tiktok 3, whatsapp 7, youtube 8) | ✅ |
| Error-wrap sites (`_handle_api_error`) | ~81 | 81 (x 8, discord 2, telegram 6, facebook 15, instagram 11, linkedin 12, threads 7, tiktok 5, whatsapp 7, youtube 8) | ✅ |
| `ensure_authenticated()` call sites | 55 across 7 | 55 (tiktok 4, whatsapp 7, threads 6, linkedin 7, youtube 7, facebook 15, instagram 9); x/discord/telegram 0 | ✅ |
| Disconnect-hook platforms | 7 call `client.disconnect()` | 7 (x, discord, facebook, instagram, linkedin, whatsapp, youtube); tiktok/telegram/threads do not | ✅ |
| `raise_authentication_error_from_manager` call sites | 10 (1/platform) | 10 | ✅ |
| Not-supported methods | 12+ (plan U9 names 15) | 15 (tiktok 4, discord 1, telegram 2, instagram 2, threads 1, whatsapp 3, youtube 2) | ✅ |
| Guard templates per platform; tiktok/threads two each | tiktok 2, threads 2, others 1 | Confirmed exactly | ✅ |
| Dialect split | auto-auth 2, assert 1, ensure 7 | Confirmed via `ensure_authenticated`/`self.authenticate()`/`_authenticated` signals | ✅ |
| Client-check-only exceptions | discord 1, instagram 2, linkedin 4–5, youtube 1 | discord `create_embed`; instagram `create_carousel`/`publish_media`; linkedin `like`/`reply`/`share`/`delete`/**`delete_reply`** (5 — plan text lists 4); youtube `delete` | ✅ (linkedin count 5, one more than the plan's prose) |

**Discrepancy (documented, not a failure):** the plan's prose lists linkedin's
client-check-only exceptions as `like`/`reply`/`share`/`delete`; the audit finds
`delete_reply` is also client-check-only (e, no ensure) — 5 methods, not 4. U5's
wrap-parity table must include it. No other reconciliation deviations.

---

## Per-Method Exception Summary (U9 guard-skip input)

Methods whose guard sequence differs from their platform's dominant shape — each is a
candidate for an explicit R10 opt-out declaration:

**Auto-auth platforms (discord, telegram)** — dominant a+e(+f)(+g):
- discord `create_embed` — **e only, sync** (opt-out: no auth-attempt, no rate-limit, no wrap)
- discord `get_post`, `list_posts` — dominant **plus g** (wrap-bearing; keep g)
- discord `share` — **h** not-supported (guard-skip)
- telegram `get_bot_info` — a+e+g, **no rate limit** (opt-out: rate-limit skip)
- telegram `reply` — a+e only, delegates for f/g (keep a+e; delegation re-runs stack)
- telegram `post`, `delete` — **h** guard-less validation+delegation (guard-skip)
- telegram `like`, `share` — **h** not-supported (guard-skip)

**Assert platform (x)** — dominant b+f+g, uniform across all 8 operations:
- no exceptions (keep b on all 8)

**Ensure platforms** — dominant c(+d)+e(+f)+g:
- instagram `create_carousel`, `publish_media` — **e only** for the auth guard (opt-out: no ensure)
- instagram `like`, `share` — **h** not-supported (guard-skip)
- linkedin `like`, `reply` — **e\* only** (opt-out: no ensure)
- linkedin `share`, `delete`, `delete_reply` — **e only** (opt-out: no ensure)
- threads `get_profile` — **d only** for guards, e-inner, g, **no rate limit** (opt-out: no ensure, rate-limit skip)
- threads `post`, `share` — **h** delegation (guard-skip)
- threads `like` — **h** not-supported (guard-skip)
- tiktok `get_creator_info` — **h** delegation (guard-skip)
- tiktok `refresh_creator_info` — c+d+e, **no rate limit**, **selective wrap** (keep selective re-raise; rate-limit skip)
- tiktok `post`, `like`, `delete`, `share` — **h** not-supported (guard-skip)
- whatsapp `reply` — **h** delegation (guard-skip)
- whatsapp `like`, `delete`, `share` — **h** not-supported (guard-skip)
- youtube `delete` — **e only** (opt-out: no ensure)
- youtube `post`, `share` — **h** not-supported (guard-skip)

**Guard-skip total for U9:** 15 not-supported methods (tiktok post/like/delete/share,
discord share, telegram like/share, instagram like/share, threads like, whatsapp
like/delete/share, youtube post/share) — matching the plan's U9 sweep list exactly.

---

## Notes for Later Units

- **U2 (wrap scope):** every g site sits around the client-call segment; guard raises
  (a/b/c/d/e) are outside all try blocks — the decorator split mirrors this cleanly.
  `_handle_api_error` chains `from error` (core `api_base.py:116`) — the U2 chained-cause
  mandate applies to the wrap decorator's re-raise, not today's code.
- **U4 (telegram):** `reply` → `send_media_group`/`send_photo`/`send_video`/`send_message`
  and `post` → `send_message`, `delete` → `delete_message` mean a whole-body wrap on the
  delegates must not double-wrap when called via the dispatchers (today: dispatchers have
  no wrap of their own; delegates wrap once).
- **U4 (x):** `validate_text` runs **outside** the try in `post` — `TextValidationError`
  already surfaces unmodified today, matching plan U4's wrap-scope requirement with no
  behavior change. `list_posts`' user-id resolution (`"Unable to resolve X user id for
  list-posts."`) runs **inside** the try — it is sanitized-and-chained by g today
  (surfaces as `"X list-posts failed: Unable to resolve X user id for list-posts."`);
  the wrap-parity gate must keep it wrapped.
- **U5 (facebook):** 15 wrap sites; `get_page_token`'s `"Facebook access token not
  available"` and `upload_regular_video`'s `"Facebook app ID is required..."` raise inside/
  beside the try — they are **wrapped** today (`_handle_api_error` re-raises). Preserve.
- **U6 (forwarders):** tiktok reads `self.access_token` at 4 guard sites; threads at 6
  (`get_profile`, `create_post`, `create_video_post`, `repost_post`, `delete`, `get_post`,
  `list_posts` — 7); these internal reads must port to `self.auth_manager` before deletion.
- **U7 (disconnect dedupe):** 7 platforms call `client.disconnect()`; tiktok/telegram/
  threads do not — threads additionally skips clearing `auth_manager.access_token`.
  discord/telegram `authenticate` have the extra post-auth client-availability raise
  (`"<Platform> client not available after authentication"`) — a base hook if collapsed.
- **Coverage baseline:** `.lcov` per-module numbers are not re-measured here (U1 scope is
  guard inventory); U3's coverage-gate baseline should be taken from the repo's `.lcov`
  at migration time.