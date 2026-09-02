#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrapper skeleton byte-parity verification (plan U6).

Machine-checks the hoisted wrapper skeleton against the invariants the
migration must preserve, per platform (or all ten when no args given):

  1. Guard messages: the literal "<Platform> API not initialized" no longer
     appears in a migrated wrapper (the base `_require_api` generates it);
     un-migrated wrappers still contain it.
  2. Import seams: `main` and `main_async` are importable from the wrapper
     module (CLI and tests depend on them).
  3. Proxy flags: the four pure-proxy platforms set `_proxy_delete_reply`;
     the others do not.
  4. Real-logic overrides: facebook/instagram/linkedin/youtube still define
     `delete_reply`; tiktok/whatsapp do not (base raise applies).
  5. Teardown: migrated wrappers do not define `disconnect` (base default).
  6. Threads variant: threads still defines its own `_is_uncertain_publish_error`
     (not byte-identical to x; must not adopt the core copy).

Exit code 0 when every checked platform passes; 1 otherwise. Usable per
platform during rollout and for the full tree at the end.
"""

import argparse
import importlib
import re
import sys
from pathlib import Path

WRAPPER_DIR = Path("packages/platforms/src/agoras/platforms")

PROXY_PLATFORMS = {"x", "discord", "telegram", "threads"}
REAL_DELETE_REPLY = {"facebook", "instagram", "linkedin", "youtube"}
THREADS_VARIANT = {"threads"}


def check_platform(name):
    failures = []
    wrapper = WRAPPER_DIR / name / "wrapper.py"
    src = wrapper.read_text()

    # 1. Guard message literal
    literal = f"{name.capitalize()} API not initialized"
    # x's class is "X", discord "Discord", etc. — map class names
    class_name = {"x": "X"}.get(name, name.capitalize())
    literal = f"{class_name} API not initialized"
    if "self._require_api()" in src:
        if literal in src:
            failures.append(f"guard literal '{literal}' still present in migrated wrapper")
    else:
        if "self._require_api()" not in src and literal not in src:
            failures.append(f"guard literal '{literal}' absent but wrapper not migrated")

    # 2. Import seams
    try:
        mod = importlib.import_module(f"agoras.platforms.{name}.wrapper")
        importlib.reload(mod)
        if not hasattr(mod, "main") or not hasattr(mod, "main_async"):
            failures.append(f"main/main_async not importable from {name}.wrapper")
    except Exception as e:  # noqa: BLE001
        failures.append(f"import failed for {name}.wrapper: {e}")

    # 3. Proxy flags
    proxy_expected = name in PROXY_PLATFORMS
    proxy_set = "_proxy_delete_reply = True" in src
    if proxy_expected and not proxy_set:
        failures.append(f"{name} is a proxy platform but _proxy_delete_reply not set")
    if not proxy_expected and proxy_set:
        failures.append(f"{name} is not a proxy platform but _proxy_delete_reply is set")

    # 4. Real-logic overrides
    if name in REAL_DELETE_REPLY:
        if not re.search(r"async def delete_reply", src):
            failures.append(f"{name} lost its real delete_reply override")
    else:
        if re.search(r"async def delete_reply", src):
            failures.append(f"{name} still defines delete_reply (should inherit base raise)")

    # 5. Teardown inherited
    if re.search(r"async def disconnect", src):
        failures.append(f"{name} still defines disconnect (should inherit base default)")

    # 6. Threads variant
    if name in THREADS_VARIANT:
        if "_is_uncertain_publish_error" not in src:
            failures.append(f"{name} lost its _is_uncertain_publish_error variant")

    return failures


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("platforms", nargs="*", help="platform names; default: all ten")
    args = parser.parse_args()

    platforms = args.platforms or [
        "x", "discord", "telegram", "threads",
        "facebook", "instagram", "linkedin", "youtube",
        "tiktok", "whatsapp",
    ]

    all_failures = []
    for name in platforms:
        failures = check_platform(name)
        if failures:
            for f in failures:
                print(f"[FAIL] {name}: {f}")
                all_failures.append((name, f))
        else:
            print(f"[PASS] {name}")

    if all_failures:
        print(f"\n{len(all_failures)} failure(s)")
        return 1
    print("\nAll checked platforms pass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())