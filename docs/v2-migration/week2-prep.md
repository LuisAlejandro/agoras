# Week 2 Preparation: Core Logic & Interfaces

**Target**: Extract agoras-core and begin agoras-platforms
**Estimated Complexity**: High
**Files to Migrate**: ~61 files

## agoras-core Extraction Plan

### Files to Extract (Week 2, Day 1-2)

#### Core Interfaces and Base Classes (3 files)

1. **base.py** → `packages/core/src/agoras/core/interfaces.py`
   - Lines: ~430
   - Current: `agoras/core/base.py`
   - Imports to update:
     - `from agoras.core.feed import Feed` → no change (stays in core)
     - `from agoras.core.media import MediaFactory` → `from agoras.media import MediaFactory`
     - `from agoras.core.sheet import ScheduleSheet` → no change (stays in core)

2. **api/base.py** → `packages/core/src/agoras/core/api_base.py`
   - Lines: ~165
   - Current: `agoras/core/api/base.py`
   - Imports: None (self-contained)

3. ****init**.py** → `packages/core/src/agoras/core/__init__.py`
   - New file to create
   - Exports: SocialNetwork, BaseAPI, Feed, Sheet, Auth classes

#### Feed Module (3 files)

- `agoras/core/feed/feed.py` → `packages/core/src/agoras/core/feed/feed.py`
- `agoras/core/feed/item.py` → `packages/core/src/agoras/core/feed/item.py`
- `agoras/core/feed/manager.py` → `packages/core/src/agoras/core/feed/manager.py`
- `agoras/core/feed/__init__.py` → `packages/core/src/agoras/core/feed/__init__.py`

**Imports to update**:

- `from agoras import __version__` → `from agoras.common import __version__`
- `from agoras.core.utils import add_url_timestamp` → `from agoras.common.utils import add_url_timestamp`

#### Sheet Module (4 files)

- `agoras/core/sheet/sheet.py` → `packages/core/src/agoras/core/sheet/sheet.py`
- `agoras/core/sheet/schedule.py` → `packages/core/src/agoras/core/sheet/schedule.py`
- `agoras/core/sheet/row.py` → `packages/core/src/agoras/core/sheet/row.py`
- `agoras/core/sheet/manager.py` → `packages/core/src/agoras/core/sheet/manager.py`
- `agoras/core/sheet/__init__.py` → `packages/core/src/agoras/core/sheet/__init__.py`

**Imports**: None expected (self-contained)

#### Auth Infrastructure (4 files → core)

These stay in core as base classes:

- `agoras/core/api/auth/base.py` → `packages/core/src/agoras/core/auth/base.py`
- `agoras/core/api/auth/storage.py` → `packages/core/src/agoras/core/auth/storage.py`
- `agoras/core/api/auth/callback_server.py` → `packages/core/src/agoras/core/auth/callback_server.py`
- `agoras/core/api/auth/exceptions.py` → `packages/core/src/agoras/core/auth/exceptions.py`
- `agoras/core/api/auth/__init__.py` → `packages/core/src/agoras/core/auth/__init__.py`

**Total for agoras-core**: ~14-15 files

## agoras-platforms Extraction Plan

### Files to Extract (Week 2, Day 3-5)

#### Platform Files (10 platforms × 4 layers = 40 files)

**Platforms**: discord, facebook, instagram, linkedin, telegram, threads, tiktok, whatsapp, x, youtube

**For each platform** (example: facebook):

1. **Wrapper**: `agoras/core/facebook.py` → `packages/platforms/src/agoras/platforms/facebook/wrapper.py`
2. **API Manager**: `agoras/core/api/facebook.py` → `packages/platforms/src/agoras/platforms/facebook/api.py`
3. **Client**: `agoras/core/api/clients/facebook.py` → `packages/platforms/src/agoras/platforms/facebook/client.py`
4. **Auth**: `agoras/core/api/auth/facebook.py` → `packages/platforms/src/agoras/platforms/facebook/auth.py`
5. ****init**.py**: New file → `packages/platforms/src/agoras/platforms/facebook/__init__.py`

**Total for agoras-platforms**: ~45-50 files (40 platform files + wrappers)

### Import Updates Required

#### For Core Package

```python
# base.py (interfaces.py)
from agoras.core.media import MediaFactory
# Change to:
from agoras.media import MediaFactory

# feed/item.py
from agoras.core.utils import add_url_timestamp
# Change to:
from agoras.common.utils import add_url_timestamp

# feed/feed.py
from agoras import __version__
# Change to:
from agoras.common import __version__
```

#### For Platforms Package

```python
# Each platform wrapper
from agoras.core.base import SocialNetwork
# Change to:
from agoras.core.interfaces import SocialNetwork

# Each API manager
from agoras.core.api.base import BaseAPI
# Change to:
from agoras.core.api_base import BaseAPI

# Each auth manager
from agoras.core.api.auth.base import BaseAuthManager
# Change to:
from agoras.core.auth.base import BaseAuthManager
```

## Week 2 Timeline

### Day 1: Core Interfaces (6-8 hours)

- Extract base.py → interfaces.py
- Extract api/base.py → api_base.py
- Extract auth base classes
- Update imports in extracted files
- Create **init**.py for core

### Day 2: Feed & Sheet (6-8 hours)

- Extract feed/ directory (4 files)
- Extract sheet/ directory (5 files)
- Update imports to use agoras.common
- Migrate feed/sheet tests
- Verify core package installs

### Day 3-4: Platforms Setup (10-12 hours)

- Create platform subdirectories (10 platforms)
- Extract first platform (facebook) as template:
  - wrapper.py
  - api.py
  - client.py
  - auth.py
  - **init**.py
- Migrate remaining 9 platforms
- Update all imports

### Day 5: Platform Testing (4-6 hours)

- Create tests for each platform
- Verify all platforms instantiate
- Run integration tests
- Document Week 2 results

## Estimated Metrics

### Lines of Code

- **agoras-core**: ~2,000 lines
  - base.py: 430 lines
  - api/base.py: 165 lines
  - feed/: 200 lines
  - sheet/: 300 lines
  - auth/: 800 lines
  - **init** files: 100 lines

- **agoras-platforms**: ~4,000 lines
  - 10 platforms × 400 lines average = 4,000 lines

### Test Coverage Goals

- **agoras-core**: 70% (critical interfaces)
- **agoras-platforms**: 40% (integration-focused)

## Risks and Challenges

### High Risk

1. **Many import updates**: 40+ files need import path changes
2. **Platform complexity**: 10 platforms with different APIs
3. **Auth integration**: OAuth flows across platforms

### Medium Risk

1. **Test migration**: Existing platform tests need updating
2. **Dependency management**: Complex web of platform SDKs

### Low Risk

1. **Feed/Sheet extraction**: Self-contained modules
2. **Core interfaces**: Clean abstractions

## Mitigation Strategies

1. **Extract incrementally**: Do one platform at a time
2. **Test frequently**: Verify after each platform
3. **Use templates**: First platform (facebook) becomes template for others
4. **Automate imports**: Use find-replace scripts for common patterns

## Success Criteria

By end of Week 2, we should have:

- ✅ agoras-core extracted and tested
- ✅ agoras-platforms structure created with all 10 platforms
- ✅ All imports updated
- ✅ Tests migrated and passing
- ✅ 4/5 packages complete (80%)
- ✅ Ready for Week 3 CLI extraction

## Conclusion

Week 2 is the **most complex week** of the migration, involving ~55-60 files and significant import updates. However, the groundwork from Week 1 (clean dependency chain, working namespace packages) provides a solid foundation for success.
