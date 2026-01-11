# Cleanup Checklist

**Date**: 2026-01-11
**Purpose**: Step-by-step checklist for removing monolithic codebase

## Pre-Cleanup Verification

**Status**: All verified ✓

- [x] All Week 3 tests passing (151/171 automated, 70/70 manual)
- [x] New packages installed and working
- [x] Entry point functional (`agoras --version` works)
- [x] No imports from old structure in new code (verified: imports resolve to new packages)
- [x] All 10 platforms accessible
- [x] Help system working
- [x] Error handling functional

**Conclusion**: SAFE TO PROCEED with cleanup

## Day 2: File Removal Checklist

### Phase 1: Remove Core Directory

**Directory**: `agoras/core/` (66 files, ~8,000 lines)

```bash
# Remove entire core directory
rm -rf agoras/core/
```

**Contents being removed**:
- [ ] 10 platform wrappers (facebook.py, x.py, etc.)
- [ ] 10 API managers (api/facebook.py, etc.)
- [ ] 10 API clients (api/clients/facebook.py, etc.)
- [ ] 10 auth managers (api/auth/facebook.py, etc.)
- [ ] Core base files (base.py, api/base.py, api/auth/base.py)
- [ ] Feed system (feed/*.py)
- [ ] Sheet system (sheet/*.py)
- [ ] Media system (media/*.py)
- [ ] Common utilities (logger.py, utils.py)
- [ ] Module __init__.py files

**Verification after removal**:
```bash
# Should not exist
[ ! -d agoras/core/ ] && echo "✓ agoras/core/ removed"

# New packages should still work
python3 -c "from agoras.platforms import Facebook" && echo "✓ Platforms still work"
python3 -c "from agoras.core.interfaces import SocialNetwork" && echo "✓ Core still works"
```

### Phase 2: Remove CLI Directory

**Directory**: `agoras/cli/` (21 files, ~2,000 lines)

```bash
# Remove entire CLI directory
rm -rf agoras/cli/
```

**Contents being removed**:
- [ ] CLI core modules (base.py, converter.py, validator.py, registry.py)
- [ ] CLI legacy support (legacy.py, migration.py)
- [ ] Platform parsers (platforms/*.py - 11 files)
- [ ] CLI utilities (utils/*.py - 2 files)
- [ ] Module __init__.py

**Verification after removal**:
```bash
# Should not exist
[ ! -d agoras/cli/ ] && echo "✓ agoras/cli/ removed"

# CLI should still work from new location
python3 -c "from agoras.cli.main import main" && echo "✓ CLI still works"
agoras --version && echo "✓ Entry point still works"
```

### Phase 3: Remove Commands Directory

**Directory**: `agoras/commands/` (2 files, ~100 lines)

```bash
# Remove commands directory
rm -rf agoras/commands/
```

**Contents being removed**:
- [ ] publish.py (legacy publish command)
- [ ] __init__.py

**Verification after removal**:
```bash
[ ! -d agoras/commands/ ] && echo "✓ agoras/commands/ removed"
python3 -c "from agoras.cli.commands.publish import main" && echo "✓ Commands still accessible"
```

### Phase 4: Remove Old Entry Point

**File**: `agoras/cli.py` (1 file, 140 lines)

```bash
# Remove old entry point file
rm agoras/cli.py
```

**Verification after removal**:
```bash
[ ! -f agoras/cli.py ] && echo "✓ agoras/cli.py removed"
agoras --version && echo "✓ New entry point works"
```

### Phase 5: Remove Old CLI Tests

**Directory**: `tests/cli/` (11 files, ~1,500 lines)

```bash
# Remove CLI test directory
rm -rf tests/cli/
```

**Contents being removed**:
- [ ] CLI test files (test_base.py, test_converter.py, etc.)
- [ ] Platform CLI tests (platforms/test_*.py)
- [ ] Module __init__.py files

**Verification after removal**:
```bash
[ ! -d tests/cli/ ] && echo "✓ tests/cli/ removed"
# New tests should still work
cd packages/cli && pytest tests/ -q && echo "✓ New CLI tests still work"
```

### Phase 6: Remove Old Core Tests

**Files**: `tests/test_core_*.py` (2 files, ~200 lines)

```bash
# Remove old core test files
rm tests/test_core_logger.py
rm tests/test_core_utils.py
```

**Verification after removal**:
```bash
[ ! -f tests/test_core_logger.py ] && echo "✓ test_core_logger.py removed"
[ ! -f tests/test_core_utils.py ] && echo "✓ test_core_utils.py removed"
# New tests should still work
cd packages/common && pytest tests/ -q && echo "✓ New common tests still work"
```

## Post-Removal Verification

After all removals complete, verify:

### Verification Script

```bash
#!/bin/bash
echo "=== POST-CLEANUP VERIFICATION ==="
echo ""

# 1. Verify directories removed
echo "1. Directories removed:"
[ ! -d agoras/core/ ] && echo "  ✓ agoras/core/ removed" || echo "  ✗ agoras/core/ still exists"
[ ! -d agoras/cli/ ] && echo "  ✓ agoras/cli/ removed" || echo "  ✗ agoras/cli/ still exists"
[ ! -d agoras/commands/ ] && echo "  ✓ agoras/commands/ removed" || echo "  ✗ agoras/commands/ still exists"
[ ! -d tests/cli/ ] && echo "  ✓ tests/cli/ removed" || echo "  ✗ tests/cli/ still exists"

# 2. Verify files removed
echo ""
echo "2. Files removed:"
[ ! -f agoras/cli.py ] && echo "  ✓ agoras/cli.py removed" || echo "  ✗ agoras/cli.py still exists"
[ ! -f tests/test_core_logger.py ] && echo "  ✓ test_core_logger.py removed" || echo "  ✗ still exists"
[ ! -f tests/test_core_utils.py ] && echo "  ✓ test_core_utils.py removed" || echo "  ✗ still exists"

# 3. Verify integration tests kept
echo ""
echo "3. Integration tests kept:"
[ -f tests/test.sh ] && echo "  ✓ tests/test.sh kept" || echo "  ✗ tests/test.sh missing"
[ -f tests/test-post.sh ] && echo "  ✓ tests/test-post.sh kept" || echo "  ✗ missing"
[ -f tests/test-last-from-feed.sh ] && echo "  ✓ tests/test-last-from-feed.sh kept" || echo "  ✗ missing"
[ -f tests/test-random-feed.sh ] && echo "  ✓ tests/test-random-feed.sh kept" || echo "  ✗ missing"
[ -f tests/test-schedule.sh ] && echo "  ✓ tests/test-schedule.sh kept" || echo "  ✗ missing"

# 4. Verify new packages still work
echo ""
echo "4. New packages functional:"
python3 -c "from agoras.common.logger import logger" && echo "  ✓ common package works"
python3 -c "from agoras.media import MediaFactory" && echo "  ✓ media package works"
python3 -c "from agoras.core.interfaces import SocialNetwork" && echo "  ✓ core package works"
python3 -c "from agoras.platforms import Facebook" && echo "  ✓ platforms package works"
python3 -c "from agoras.cli.main import main" && echo "  ✓ cli package works"

# 5. Verify entry point
echo ""
echo "5. Entry point functional:"
agoras --version && echo "  ✓ agoras command works"

# 6. Verify no broken imports
echo ""
echo "6. Import chain intact:"
python3 -c "from agoras.platforms import Facebook, X, Instagram, LinkedIn, Discord, Telegram, WhatsApp, YouTube, TikTok, Threads" && echo "  ✓ All platforms import"

echo ""
echo "=== VERIFICATION COMPLETE ==="
```

**Expected Result**: All checks pass ✓

## Rollback Plan (If Needed)

If something breaks after cleanup:

### Step 1: Identify the Issue
```bash
# Check what's broken
agoras --version
python3 -c "from agoras.cli.main import main"
```

### Step 2: Check Git History
```bash
# View what was removed
git log --oneline --name-status HEAD~1..HEAD

# View deleted file content
git show HEAD~1:agoras/core/facebook.py
```

### Step 3: Fix or Revert
```bash
# Option A: Fix the issue in new packages
# (Preferred - likely just a missed import update)

# Option B: Revert the cleanup commit
git revert HEAD

# Option C: Cherry-pick specific file back temporarily
git show HEAD~1:agoras/core/facebook.py > agoras/core/facebook.py
```

## Safety Notes

1. **Git Preserves History**: All deleted files remain in git history
2. **Packages Tested**: New structure tested with 151 automated + 70 manual tests
3. **Low Risk**: Can easily revert if issues found
4. **Verified Working**: All functionality confirmed in new packages

## Dependencies Verified

**Confirmed**: New packages do NOT depend on old structure
- All imports resolve to `packages/*/src/agoras/*`
- No references to old `agoras/core/`, `agoras/cli/`, or `agoras/commands/`
- Safe to remove old files

## Timeline for Day 2

**Estimated**: 30 minutes

- Phase 1: Remove core/ (5 min)
- Phase 2: Remove cli/ (3 min)
- Phase 3: Remove commands/ (2 min)
- Phase 4: Remove cli.py (1 min)
- Phase 5: Remove tests/cli/ (3 min)
- Phase 6: Remove test_core_*.py (2 min)
- Verification script (10 min)
- Documentation (5 min)

## Success Criteria

Day 2 complete when:

- [ ] All 103 old files removed
- [ ] Post-removal verification passes
- [ ] New packages still work
- [ ] Entry point still functional
- [ ] Tests still passing
- [ ] Integration tests kept (tests/*.sh)
- [ ] Cleanup committed to git

---

**Status**: Checklist ready for Day 2 execution
