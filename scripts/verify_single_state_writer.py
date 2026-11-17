#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Single-state-writer gate: one stored state per machine, one function that writes it.

Each entry in ``MACHINES`` declares, for one class, the attributes that encode
its lifecycle and the transition method allowed to write them. The gate fails
when any other method assigns one of those attributes, which is how a machine
grows a second source of truth (a boolean that can disagree with the state, or
a flag written before the state it describes).

Assignments allowed without declaration:

* ``__init__`` -- the initial value.
* ``@<attr>.setter`` -- a property setter, the migration bridge that keeps an
  old boolean name working while call sites move to the transition method.

Machines absent from ``MACHINES`` are skipped, so the table ratchets: the gate
never blocks a machine that has not been migrated yet.

Exit code 0 when every declared machine has a single writer; 1 otherwise.
"""

import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TREES = [
    "packages/common/src/agoras",
    "packages/media/src/agoras",
    "packages/core/src/agoras",
    "packages/platforms/src/agoras",
    "packages/cli/src/agoras",
]

# class name -> (state attributes, transition method names)
_CLIENT = (frozenset({"_auth_state", "_authenticated"}), frozenset({"_set_auth_state"}))

MACHINES = {
    "Media": (frozenset({"_state", "_downloaded", "_is_local"}), frozenset({"_set_state"})),
    "AuthLifecycle": _CLIENT,
    "BaseAPI": _CLIENT,
    "BaseAuthManager": (
        frozenset({"_auth_state", "authenticated", "last_auth_failure"}),
        frozenset({"_record_auth_failure"}),
    ),
    "XAPIClient": _CLIENT,
    "FacebookAPIClient": _CLIENT,
    "InstagramAPIClient": _CLIENT,
    "WhatsAppAPIClient": _CLIENT,
    "LinkedInAPIClient": _CLIENT,
    "YouTubeAPIClient": _CLIENT,
    "DiscordAPIClient": _CLIENT,
    "CallbackState": (
        frozenset({"outcome", "auth_code", "callback_url", "oauth_version", "error", "settled"}),
        frozenset({"settle"}),
    ),
    "ComposerHTTPServer": (
        frozenset({"outcome", "_payload", "payload", "cancelled"}),
        frozenset({"settle", "reset"}),
    ),
    "X": (frozenset({"_subscription", "_subscription_type", "_subscription_resolved"}), frozenset({"_set_subscription"})),
    "Feed": (frozenset({"_items", "_downloaded"}), frozenset({"_set_items"})),
    "FeedItem": (frozenset({"_parsed", "_processed"}), frozenset({"_set_parsed"})),
    "ControlableLogger": (frozenset({"_state", "disabled"}), frozenset({"_set_state"})),
    "DiscordAuthManager": (frozenset({"_cached_user_info"}), frozenset({"_cache_user_info"})),
}

INIT = "__init__"


def _assigned_attrs(node):
    """Yield attribute names assigned by one statement (self.x = ..., self.x += ...)."""
    if isinstance(node, ast.Assign):
        targets = node.targets
    elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
        targets = [node.target]
    else:
        targets = []
    for target in targets:
        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
            yield target.attr


def _setattr_attrs(node):
    """Yield literal attribute names passed to ``setattr(self, "<name>", ...)``."""
    for call in ast.walk(node):
        if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name):
            continue
        if call.func.id != "setattr" or len(call.args) < 2:
            continue
        owner, name = call.args[0], call.args[1]
        if isinstance(owner, ast.Name) and owner.id == "self" and isinstance(name, ast.Constant):
            if isinstance(name.value, str):
                yield name.value


def _is_property_setter(function):
    """True for ``@<name>.setter`` decorated functions."""
    for decorator in function.decorator_list:
        if isinstance(decorator, ast.Attribute) and decorator.attr == "setter":
            return True
    return False


def _scan_function(class_name, function, state_attrs, transitions, filename, failures):
    """Report every write to a state attribute this function is not allowed to make."""
    if function.name == INIT or function.name in transitions or _is_property_setter(function):
        return
    for statement in function.body:
        for node in ast.walk(statement):
            candidates = list(_assigned_attrs(node)) + list(_setattr_attrs(node))
            for attr in candidates:
                if attr in state_attrs:
                    allowed = ", ".join(sorted(transitions | {INIT, "property setters"}))
                    failures.append(
                        f"{filename}:{class_name}.{attr} assigned in {function.name}() "
                        f"-- route it through the transition method (allowed: {allowed})"
                    )


def check_source(source, filename):
    """Return the failure list for one module's source text."""
    failures = []
    tree = ast.parse(source, filename=filename)
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef) or node.name not in MACHINES:
            continue
        state_attrs, transitions = MACHINES[node.name]
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                _scan_function(node.name, item, state_attrs, transitions, filename, failures)
    return failures


def declared_classes(source):
    """Return the MACHINES class names defined in one module's source text."""
    return {node.name for node in ast.walk(ast.parse(source)) if isinstance(node, ast.ClassDef)} & set(MACHINES)


def run_gate():
    """Scan every declared machine in the source trees; return the failures."""
    failures = []
    found = set()
    for tree in TREES:
        for path in sorted((ROOT / tree).rglob("*.py")):
            relative = path.relative_to(ROOT)
            source = path.read_text(encoding="utf-8")
            found |= declared_classes(source)
            failures.extend(check_source(source, str(relative)))
    for name in sorted(set(MACHINES) - found):
        failures.append(f"{name}: declared in MACHINES but no class of that name was found in the source trees")
    return failures


def self_test():
    """Negative self-test: the scanner must flag a second writer and clear a single one."""
    failures = []

    illegal = '''
class Media:
    def __init__(self):
        self._state = "new"

    def _set_state(self, state):
        self._state = state

    def download(self):
        self._state = "downloaded"
        self._downloaded = True
'''
    flagged = check_source(illegal, "illegal_mod.py")
    if not any("Media._state assigned in download()" in f for f in flagged):
        failures.append("self-test: direct state write in a non-transition method was not flagged")
    if not any("Media._downloaded assigned in download()" in f for f in flagged):
        failures.append("self-test: derived-flag write in a non-transition method was not flagged")
    if any("Media._state assigned in _set_state()" in f for f in flagged):
        failures.append("self-test: the declared transition method was flagged")

    legal = '''
class Media:
    def __init__(self):
        self._state = "new"

    def _set_state(self, state, **fields):
        for name, value in fields.items():
            setattr(self, name, value)
        self._state = state

    @property
    def _downloaded(self):
        return self._state == "downloaded"

    @_downloaded.setter
    def _downloaded(self, value):
        self._state = "downloaded" if value else "new"

    def cleanup(self):
        self._set_state("cleaned")
        self.temp_file = None
'''
    if check_source(legal, "legal_mod.py"):
        failures.append(f"self-test: compliant machine was flagged: {check_source(legal, 'legal_mod.py')}")

    undeclared = '''
class NotAMachine:
    def poke(self):
        self._state = "whatever"
'''
    if check_source(undeclared, "undeclared_mod.py"):
        failures.append("self-test: an undeclared class was scanned (the table must ratchet)")

    if not failures:
        print("Self-test passed: the gate flags a second writer and clears a single one.")
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

    failures = run_gate()
    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        print(f"\n{len(failures)} failure(s)")
        return 1
    print(f"Single state writer verified for {len(MACHINES)} machine(s): {', '.join(sorted(MACHINES))}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
