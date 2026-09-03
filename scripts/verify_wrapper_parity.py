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
CLASS_NAMES = {
    "x": "X",
    "discord": "Discord",
    "telegram": "Telegram",
    "threads": "Threads",
    "facebook": "Facebook",
    "instagram": "Instagram",
    "linkedin": "LinkedIn",
    "youtube": "YouTube",
    "tiktok": "TikTok",
    "whatsapp": "WhatsApp",
}


def check_proxy_flags(name, src, failures):
    proxy_expected = name in PROXY_PLATFORMS
    proxy_set = "_proxy_delete_reply = True" in src
    if proxy_expected and not proxy_set:
        failures.append(f"{name} is a proxy platform but _proxy_delete_reply not set")
    if not proxy_expected and proxy_set:
        failures.append(f"{name} is not a proxy platform but _proxy_delete_reply is set")
    if name == "telegram":
        if "_proxy_get_reply" in src:
            failures.append("telegram must not proxy get_reply (no get_post support)")
    elif proxy_expected and "_proxy_get_reply = True" not in src:
        failures.append(f"{name} is a proxy platform but _proxy_get_reply not set")


def check_overrides(name, src, failures):
    if name in REAL_DELETE_REPLY:
        if not re.search(r"async def delete_reply", src):
            failures.append(f"{name} lost its real delete_reply override")
    else:
        if re.search(r"async def delete_reply", src):
            failures.append(f"{name} still defines delete_reply (should inherit base raise)")
    if re.search(r"async def disconnect", src):
        failures.append(f"{name} still defines disconnect (should inherit base default)")
    if name in THREADS_VARIANT and "_is_uncertain_publish_error" not in src:
        failures.append(f"{name} lost its _is_uncertain_publish_error variant")


CHECK_IMPORTS = False


def check_wrapper_source(name, src):
    """Run all structural checks against a wrapper module's source text."""
    failures = []

    # 1. Guard message literal (real class names — capitalize() is wrong
    # for youtube/tiktok/linkedin/whatsapp)
    literal = f"{CLASS_NAMES[name]} API not initialized"
    if "self._require_api()" in src:
        if literal in src:
            failures.append(f"guard literal '{literal}' still present in migrated wrapper")
    else:
        failures.append(f"{name} does not use _require_api (guard migration incomplete)")

    # 2. Import seams (requires the installed packages + SDK deps)
    if CHECK_IMPORTS:
        try:
            mod = importlib.import_module(f"agoras.platforms.{name}.wrapper")
            importlib.reload(mod)
            if not hasattr(mod, "main") or not hasattr(mod, "main_async"):
                failures.append(f"main/main_async not importable from {name}.wrapper")
        except Exception as e:  # noqa: BLE001
            failures.append(f"import failed for {name}.wrapper: {e}")
    else:
        # Offline structural check: the module defines main/main_async
        if "def main(" not in src or "async def main_async(" not in src:
            failures.append(f"main/main_async not defined in {name}.wrapper")

    # 3-6. Proxy flags, overrides, teardown, threads variant
    check_proxy_flags(name, src, failures)
    check_overrides(name, src, failures)

    # 7. Unbound-dispatch coupling guard: a wrapper subclass defining
    # run_main_async would be silently bypassed by the unbound shims.
    if re.search(r"async def run_main_async", src):
        failures.append(f"{name} defines run_main_async — would be bypassed by the unbound shims")

    return failures


def self_test():
    """Negative self-test: the checks must fail on unmigrated/regressed sources."""
    failures = []
    unmigrated = (
        "class X(SocialNetwork):\n"
        "    async def disconnect(self):\n"
        "        if self.api:\n"
        "            await self.api.disconnect()\n"
        "    async def post(self, *a):\n"
        "        if not self.api:\n"
        '            raise Exception("X API not initialized")\n'
        "        return 1\n"
    )
    f = check_wrapper_source("x", unmigrated)
    if not any("_require_api" in item for item in f):
        failures.append("self-test: unmigrated wrapper not flagged")
    if not any("disconnect" in item for item in f):
        failures.append("self-test: inherited-disconnect regression not flagged")
    overridden = (
        "class X(SocialNetwork):\n"
        "    _proxy_delete_reply = True\n"
        "    _proxy_get_reply = True\n"
        "    async def run_main_async(self, kwargs):\n"
        "        return 0\n"
        "    def main(self):\n"
        "        pass\n"
        "    async def main_async(self):\n"
        "        pass\n"
    )
    f = check_wrapper_source("x", overridden)
    if not any("run_main_async" in item for item in f):
        failures.append("self-test: run_main_async override not flagged")
    if not failures:
        print("Self-test passed: the gate catches unmigrated wrappers and bypassed overrides.")
        return 0
    for item in failures:
        print(f"[FAIL] {item}")
    return 1


def check_platform(name):
    wrapper = WRAPPER_DIR / name / "wrapper.py"
    return check_wrapper_source(name, wrapper.read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("platforms", nargs="*", help="platform names; default: all ten")
    parser.add_argument("--check-imports", action="store_true", help="also import each wrapper module (needs SDK deps)")
    parser.add_argument("--self-test", action="store_true", help="run negative self-tests and exit")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    global CHECK_IMPORTS
    CHECK_IMPORTS = args.check_imports

    platforms = args.platforms or [
        "x",
        "discord",
        "telegram",
        "threads",
        "facebook",
        "instagram",
        "linkedin",
        "youtube",
        "tiktok",
        "whatsapp",
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
