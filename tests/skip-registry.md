# Live E2E skip registry

Actions that may SKIP during runs (exit 0 for that case, suite continues).

| Platform | Action | Typical reason | Re-test trigger |
|----------|--------|----------------|-----------------|
| tiktok | post | Slideshow API not enabled, or image URL not on verified domain | TikTok scopes + URL property for `luisalejandro.org` |
| tiktok | video | Production approval not granted | App approved for video upload |
| x | video | Upload limits or media processing failure | Retry after cooldown |
| instagram | video | Reels/container API restrictions | Account or app capability change |
| discord | video | File over 8MB limit or bot upload failure | Use `TEST_DISCORD_VIDEO_URL` under 8MB |
| * | video/image | `MediaValidationError` (MIME, size, duration) | Run `agoras utils media-limits` and fix asset URL |
| linkedin | video | Video API not enabled | LinkedIn product access granted |
| threads | video | Media upload restrictions | Meta app review complete |
| telegram | video | Bot permissions or file size | Bot admin rights fixed |
| whatsapp | video | Media message policy | Business account verified |
| whatsapp | template | `WHATSAPP_TEMPLATE_NAME` unset or template not approved | Set env var + approved template |
| utils | feed-publish | Network credentials missing for target | Add creds to `unattended.env` |
| legacy publish | feed/schedule | Same triggers as utils feed-publish / schedule-run | Add creds + fixtures to `unattended.env` |
| * | tokens list | Env-only platform (x, discord, telegram, whatsapp) on unattended path | N/A — expected SKIP |
