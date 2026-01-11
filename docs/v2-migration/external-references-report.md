# External References to Old Structure

**Date**: 2026-01-11
**Purpose**: Identify files that reference the old monolithic structure and need updates

## Files Requiring Updates

### 1. setup.py (ROOT LEVEL) - CRITICAL

**File**: [`setup.py`](../../setup.py)

**Current References**:
```python
# Line 22-23: Imports from old agoras/__init__.py
from agoras import (__author__, __email__, __version__, __url__, __description__)

# Line 44: References old package structure
packages=['agoras', 'agoras.api', 'agoras.core'],

# Line 45: References old directory
package_dir={'agoras': 'agoras'},

# Line 49: Old entry point
entry_points={'console_scripts': ('agoras = agoras.cli:main',)},
```

**Action Needed** (Day 3):
```python
# Option A: Remove this file entirely (recommended)
# The CLI is now in packages/cli/setup.py with proper entry point

# Option B: Convert to meta-package that installs packages/cli
# (Not recommended - adds complexity)
```

**Priority**: HIGH - This file conflicts with new package structure

**Recommendation**: REMOVE this file in Day 3. The proper setup.py is in `packages/cli/setup.py`.

### 2. tox.ini (ROOT LEVEL)

**File**: [`tox.ini`](../../tox.ini)

**Current References**:
```ini
# Line 7: References old agoras directory
PYTHONPATH = {toxinidir}:{toxinidir}/agoras

# Line 14: Coverage for old structure  
coverage run --source agoras -m unittest -v -f
```

**Action Needed** (Day 3):
```ini
# Option A: Remove and use packages/tox.ini instead (recommended)
# packages/tox.ini is already configured for new structure

# Option B: Update to test new packages
[testenv]
changedir = {toxinidir}/packages
commands = pytest common/tests media/tests core/tests platforms/tests cli/tests -v
```

**Priority**: MEDIUM - Old tox config references old structure

**Recommendation**: REMOVE root tox.ini, use `packages/tox.ini` instead

### 3. Makefile

**File**: [`Makefile`](../../Makefile)

**Status**: Need to check if it references old structure

**Action**: Review in Day 3 and update any references to:
- Old test paths
- Old build targets
- Old coverage paths

### 4. Dockerfile

**File**: [`Dockerfile`](../../Dockerfile)

**Status**: Need to check if it references old structure

**Action**: Review in Day 3 and update any:
- COPY commands referencing agoras/
- RUN commands with old paths
- Entry point references

### 5. .gitignore

**File**: [`.gitignore`](../../.gitignore)

**Status**: Likely has patterns for old structure

**Potential References**:
```
agoras.egg-info/
*.egg-info
```

**Action**: Review and ensure patterns cover new structure:
```
packages/*/*.egg-info
packages/*/build/
packages/*/dist/
```

### 6. Documentation Files

**Files Needing Review** (Day 5):

- `README.rst` - Main documentation
- `CONTRIBUTING.rst` - Contributor guide  
- `docs/` - All documentation
- `CLI_PARAMETERS.md` - CLI reference
- `USAGE.rst` - Usage guide

**Common Issues**:
- Code examples using old imports
- File path references
- Installation instructions
- Development setup guides

**Action**: Systematic review and update in Day 5

## Files NOT Needing Updates

### Already Correct

**File**: `.github/workflows/*.yml`
**Status**: ✓ No references to old structure found

**File**: `MANIFEST.in`
**Status**: ✓ Uses generic patterns (`recursive-include tests *`)

**File**: `requirements.txt`
**Status**: ✓ Lists external dependencies only

**File**: `packages/*`
**Status**: ✓ All use new structure exclusively

## Summary of Required Actions

### Day 3: Configuration Updates

**Files to Update/Remove**:
1. `setup.py` - REMOVE (use packages/cli/setup.py)
2. `tox.ini` - REMOVE (use packages/tox.ini)
3. `Makefile` - UPDATE if it exists
4. `Dockerfile` - UPDATE if it exists
5. `.gitignore` - VERIFY patterns cover new structure

### Day 5: Documentation Updates

**Files to Update**:
1. `README.rst` - Update for modular structure
2. `CONTRIBUTING.rst` - Update development setup
3. `docs/` - Update all code examples
4. `CLI_PARAMETERS.md` - Verify still accurate
5. `USAGE.rst` - Update usage examples

## Critical Path Items

### Blocking Issues (Must Fix Before Release)

1. **Root setup.py** - Conflicts with new structure
   - **Impact**: HIGH - May cause installation issues
   - **Action**: Remove in Day 3
   - **Alternative**: Convert to meta-package (not recommended)

### Non-Blocking Items (Can Fix Later)

1. **Documentation** - Old examples still work but confusing
   - **Impact**: MEDIUM - Users may follow old patterns
   - **Action**: Update in Day 5
   - **Deadline**: Before v2.0.0 release

2. **Makefile/Dockerfile** - Build automation
   - **Impact**: LOW - Affects developers only
   - **Action**: Update in Day 3
   - **Deadline**: Before sharing with contributors

## Verification After Updates

After updating external references, verify:

```bash
# 1. Installation from root should point to packages
pip install .  # Should install from packages/cli or fail cleanly

# 2. Tox should use new structure
cd packages && tox -e all

# 3. Documentation examples should use new imports
# (Manual review)

# 4. Build tools should reference new paths
make test  # or equivalent
```

## Recommendations

### Day 3 Actions

**Remove** (Recommended):
- `setup.py` - Obsolete, conflicts with packages/cli/setup.py
- `tox.ini` - Obsolete, use packages/tox.ini

**Update** (If Present):
- `Makefile` - Point to packages/
- `Dockerfile` - Update paths
- `.gitignore` - Verify patterns

### Day 5 Actions

**Update** (Required):
- All documentation files
- Code examples  
- Import statements
- File path references

---

**Status**: External references identified and prioritized
