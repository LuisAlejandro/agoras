#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API rate-limit parity verification (QA residual: audit replay gate).

Replays the 84-site rate-limit inventory from
`rosey/audits/2026-09-02-platform-guard-audit.md` against the ten platform
api modules. For every method the audit records with a rate limit, the
implementation must throttle on the same literal bucket key with the same
interval — whether via the `@guard_rate_limit("key", interval)` decorator
or an inline `await self._rate_limit_check("key", interval)` (linkedin's
five object_id-guarded methods and whatsapp's send_template use the
inline form). This gate is what would have caught the threads
create_video_post/delete/get_post intervals dropped during the
guard-decorator rollout.

DATA LIFECYCLE: when a platform legitimately changes an interval or the
audit doc is corrected, update this inventory IN THE SAME CHANGE as the
implementation, update the audit doc to match, and re-run --self-test.
A gate failure on a legitimate change is a data update, not a code fix.

Exit code 0 when every module matches; 1 otherwise. Text-based and offline.
"""

import argparse
import re
import sys
from pathlib import Path

API_DIR = Path("packages/platforms/src/agoras/platforms")

# (method, bucket_key, interval) per platform — transcribed from the audit.
EXPECTED = {
    "x": [
        ("upload_media", "upload_media", 1.0),
        ("post", "post", 1.0),
        ("like", "like", 0.5),
        ("reply", "post", 1.0),
        ("share", "share", 0.5),
        ("delete", "delete", 0.5),
        ("get_post", "get_post", 0.5),
        ("list_posts", "list_posts", 0.5),
    ],
    "discord": [
        ("post", "post", 1.0),
        ("reply", "reply", 1.0),
        ("create_public_thread", "create_public_thread", 1.0),
        ("send_message_to_thread", "send_message_to_thread", 1.0),
        ("like", "like", 0.5),
        ("delete", "delete", 0.5),
        ("get_post", "get_post", 0.5),
        ("list_posts", "list_posts", 0.5),
        ("upload_file", "upload_file", 1.0),
    ],
    "telegram": [
        ("send_message", "send_message", 1.0),
        ("send_photo", "send_photo", 1.0),
        ("send_video", "send_video", 1.0),
        ("delete_message", "delete_message", 0.5),
        ("send_media_group", "send_media_group", 1.0),
    ],
    "facebook": [
        ("check_if_page", "check_if_page", 0.1),
        ("get_page_token", "get_page_token", 0.5),
        ("post", "post", 1.0),
        ("upload_media", "upload_media", 1.0),
        ("upload_photo_file", "upload_photo_file", 1.0),
        ("like", "like", 0.5),
        ("reply", "reply", 0.5),
        ("delete", "delete", 0.5),
        ("delete_reply", "delete", 0.5),
        ("get_post", "get_post", 0.5),
        ("get_reply", "get_reply", 0.5),
        ("list_posts", "list_posts", 0.5),
        ("share", "share", 1.0),
        ("upload_reel_or_story", "upload_reel_or_story", 1.0),
        ("upload_regular_video", "upload_regular_video", 1.0),
    ],
    "instagram": [
        ("post", "post", 1.0),
        ("create_media", "create_media", 1.0),
        ("create_resumable_video", "create_resumable_video", 1.0),
        ("create_carousel", "create_carousel", 1.0),
        ("publish_media", "publish_media", 1.0),
        ("delete", "delete", 0.5),
        ("reply", "reply", 0.5),
        ("delete_reply", "delete", 0.5),
        ("get_post", "get_post", 0.5),
        ("get_reply", "get_reply", 0.5),
        ("list_posts", "list_posts", 0.5),
    ],
    "linkedin": [
        ("upload_video", "upload_video", 2.0),
        ("upload_image", "upload_image", 1.0),
        ("post", "post", 1.0),
        ("like", "like", 0.5),
        ("reply", "reply", 0.5),
        ("share", "share_post", 1.0),
        ("delete", "delete", 0.5),
        ("delete_reply", "delete", 0.5),
        ("get_post", "get_post", 0.5),
        ("get_reply", "get_reply", 0.5),
        ("get_media", "get_media", 0.5),
        ("list_posts", "list_posts", 0.5),
    ],
    "threads": [
        ("create_post", "create_post", 2.0),
        ("create_video_post", "create_video_post", 2.0),
        ("repost_post", "repost_post", 2.0),
        ("delete", "delete_post", 1.0),
        ("get_post", "get_post", 1.0),
        ("list_posts", "list_posts", 1.0),
    ],
    "tiktok": [
        ("upload_video", "upload_video", 2.0),
        ("upload_video_file", "upload_video_file", 2.0),
        ("upload_photo", "upload_photo", 2.0),
    ],
    "whatsapp": [
        ("post", "post", 1.0),
        ("send_message", "send_message", 1.0),
        ("upload_media", "upload_media", 1.0),
        ("send_image", "send_image", 1.0),
        ("send_video", "send_video", 1.0),
        ("get_business_profile", "get_business_profile", 1.0),
        ("send_template", "send_template", 1.0),
    ],
    "youtube": [
        ("upload_video", "upload_video", 2.0),
        ("like", "like", 1.0),
        ("delete", "delete", 1.0),
        ("reply", "reply", 1.0),
        ("delete_reply", "delete", 1.0),
        ("get_post", "get_post", 1.0),
        ("get_reply", "get_reply", 1.0),
        ("list_posts", "list_posts", 1.0),
    ],
}

RATE_DECORATOR = "guard_rate_limit"


def _method_rate_limit(src, method):
    """Return (bucket_key, interval) for a method, or None if it has none.

    Accepts either the decorator form or the inline _rate_limit_check call
    within the method body.
    """
    lines = src.split("\n")
    def_lines = [
        i for i, l in enumerate(lines)
        if re.match(r"^    (async )?def " + re.escape(method) + r"\(", l)
    ]
    if not def_lines:
        return None
    dline = def_lines[0]

    # Decorator stack immediately above the def
    stack = []
    j = dline - 1
    while j >= 0 and re.match(r"^    @guard_\w+", lines[j]):
        stack.append(lines[j].strip())
        j -= 1
    for deco in stack:
        m = re.search(re.escape(RATE_DECORATOR) + r'\("([a-z_]+)", ([0-9.]+)\)', deco)
        if m:
            return (m.group(1), m.group(2))

    # Inline form within the method body (until the next top-level def)
    for line in lines[dline + 1:]:
        if re.match(r"^    (async )?def ", line):
            break
        m = re.search(r'_rate_limit_check\("([a-z_]+)", ([0-9.]+)\)', line)
        if m:
            return (m.group(1), m.group(2))
    return None


def check_api_source(name, src):
    failures = []
    for method, key, interval in EXPECTED[name]:
        found = _method_rate_limit(src, method)
        if found is None:
            failures.append(f'{name}.{method}: expected rate limit ("{key}", {interval}) but none found')
        elif found != (key, str(interval)):
            failures.append(
                f'{name}.{method}: expected ("{key}", {interval}), found ("{found[0]}", {found[1]})'
            )
    return failures


def self_test():
    failures = []
    global EXPECTED
    saved = EXPECTED

    # Scenario 1: both decorator and inline forms are valid
    fixture = (
        '    @guard_rate_limit("post", 1.0)\n'
        "    async def post(self):\n"
        "        return 1\n"
        "    async def like(self):\n"
        '        await self._rate_limit_check("like", 0.5)\n'
        "        return 1\n"
    )
    EXPECTED = {
        "fake": [
            ("post", "post", "1.0"),
            ("like", "like", "0.5"),
        ]
    }
    if check_api_source("fake", fixture):
        failures.append("self-test: valid decorator+inline forms flagged")

    # Scenario 2: a missing rate limit must be flagged
    EXPECTED = {
        "fake": [
            ("delete", "delete", "0.5"),
        ]
    }
    missing = (
        "    async def delete(self):\n"
        "        return 1\n"
    )
    f = check_api_source("fake", missing)
    if not any("expected rate limit" in item for item in f):
        failures.append("self-test: missing rate limit not flagged")

    # Scenario 3: a wrong interval must be flagged
    EXPECTED = {
        "fake": [
            ("share", "post", "2.0"),
        ]
    }
    wrong = (
        '    @guard_rate_limit("post", 1.0)\n'
        "    async def share(self):\n"
        "        return 1\n"
    )
    f = check_api_source("fake", wrong)
    if not any('expected ("post", 2.0)' in item for item in f):
        failures.append("self-test: wrong interval not flagged")

    EXPECTED = saved
    if not failures:
        print("Self-test passed: the gate catches missing and drifted rate limits.")
        return 0
    for item in failures:
        print(f"[FAIL] {item}")
    return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="run negative self-tests and exit")
    args = parser.parse_args()
    if args.self_test:
        return self_test()

    all_failures = []
    for name in EXPECTED:
        src = (API_DIR / name / "api.py").read_text()
        failures = check_api_source(name, src)
        if failures:
            for f in failures:
                print(f"[FAIL] {f}")
                all_failures.append(f)
        else:
            print(f"[PASS] {name}")

    if all_failures:
        print(f"\n{len(all_failures)} failure(s)")
        return 1
    print("\nAll api modules match the audit rate-limit inventory.")
    return 0


if __name__ == "__main__":
    sys.exit(main())