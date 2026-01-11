# Agoras Package Split Plan (True Split)

This plan details the strategy to divide the monolithic `agoras` package into 5 independent, distributable PyPI packages using a Layered Architecture.

## Objectives

- **Decoupling**: Isolate components to minimize circular dependencies.
- **Modularity**: Allow users/developers to install only specific parts (e.g., just the media handler or just the core interfaces).
- **Maintainability**: Clearer boundaries between Infrastructure, Logic, and Interfaces.

## 1. Package Architecture & Dependency Graph

The packages are organized in layers. Higher layers depend on lower layers.

```mermaid
graph TD
    CLI[agoras-cli] --> Platforms[agoras-platforms]
    Platforms --> Core[agoras-core]
    Core --> Media[agoras-media]
    Media --> Common[agoras-common]
    Core --> Common
    Platforms --> Common
    CLI --> Common
```

| Package Name | PyPI Name (Proposed) | Namespace | Purpose | Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| **Common** | `agoras-common` | `agoras.common` | Low-level utilities, logging, shared constants. | None |
| **Media** | `agoras-media` | `agoras.media` | Image and Video processing logic. | `agoras-common` |
| **Core** | `agoras-core` | `agoras.core` | Interfaces (`SocialNetwork`), Generic Logic (`Feed`, `Sheet`), Base API/Auth classes. | `agoras-common`, `agoras-media` |
| **Platforms** | `agoras-platforms` | `agoras.platforms` | Concrete API clients and `SocialNetwork` implementations. | `agoras-core` |
| **CLI** | `agoras` (or `agoras-cli`) | `agoras.cli` | Command Line Interface and entry point. | `agoras-platforms` |

*> Note: The main user-facing tool will likely retain the package name `agoras` on PyPI (containing the CLI), or `agoras-cli` if you prefer explicit naming.*

## 2. Detailed File Mapping

### 1. `agoras-common`

**Root**: `src/agoras/common`
**Description**: Pure python utilities with minimal external dependencies.

| Current File | New Location | Notes |
| :--- | :--- | :--- |
| `agoras/core/utils.py` | `agoras/common/utils.py` | Generic helper functions. |
| `agoras/core/logger.py` | `agoras/common/logger.py` | Logging configuration. |
| `agoras/__init__.py` | `agoras/common/version.py` | Version info, Author metadata (shared source of truth). |

### 2. `agoras-media`

**Root**: `src/agoras/media`
**Description**: Heavy media processing.

| Current File | New Location | Notes |
| :--- | :--- | :--- |
| `agoras/core/media/__init__.py` | `agoras/media/__init__.py` | |
| `agoras/core/media/base.py` | `agoras/media/base.py` | Base Media classes. |
| `agoras/core/media/image.py` | `agoras/media/image.py` | Image processing. |
| `agoras/core/media/video.py` | `agoras/media/video.py` | Video processing. |
| `agoras/core/media/factory.py` | `agoras/media/factory.py` | Factory pattern. |

### 3. `agoras-core`

**Root**: `src/agoras/core`
**Description**: The framework logic. Defines *how* things work abstractly.

| Current File | New Location | Notes |
| :--- | :--- | :--- |
| `agoras/core/base.py` | `agoras/core/interfaces.py` | `SocialNetwork` abstract class. |
| `agoras/core/api/base.py` | `agoras/core/api_base.py` | `BaseAPI` class. |
| `agoras/core/api/auth/base.py` | `agoras/core/auth/base.py` | `BaseAuthManager`. |
| `agoras/core/api/auth/storage.py`| `agoras/core/auth/storage.py`| Token storage logic. |
| `agoras/core/api/auth/exceptions.py`| `agoras/core/auth/exceptions.py`| Auth exceptions. |
| `agoras/core/api/auth/callback_server.py`| `agoras/core/auth/callback_server.py`| OAuth Callback Server. |
| `agoras/core/feed/*` | `agoras/core/feed/*` | Feed Logic. |
| `agoras/core/sheet/*` | `agoras/core/sheet/*` | Google Sheets Logic. |

### 4. `agoras-platforms`

**Root**: `src/agoras/platforms`
**Description**: The "drivers". Concrete implementations.

| Current File | New Location | Notes |
| :--- | :--- | :--- |
| **Wrapper Layer** | | |
| `agoras/core/<platform>.py` | `agoras/platforms/<platform>/wrapper.py` | e.g. `facebook.py`, `telegram.py`, `x.py`. |
| **API Manager Layer** | | |
| `agoras/core/api/<platform>.py` | `agoras/platforms/<platform>/api.py` | High-level API manager. |
| **Client Layer** | | |
| `agoras/core/api/clients/<platform>.py` | `agoras/platforms/<platform>/client.py` | Low-level HTTP client. |
| **Auth Layer** | | |
| `agoras/core/api/auth/<platform>.py` | `agoras/platforms/<platform>/auth.py` | Platform-specific auth logic. |

*Platforms to migrate*: `discord`, `facebook`, `instagram`, `linkedin`, `telegram`, `threads`, `tiktok`, `twitter` (legacy), `whatsapp`, `x`, `youtube`.

### 5. `agoras-cli` (The Main Package)

**Root**: `src/agoras/cli`
**Description**: The executable.

| Current File | New Location | Notes |
| :--- | :--- | :--- |
| `agoras/cli.py` | `agoras/cli/main.py` | Entry point. |
| `agoras/cli/*` | `agoras/cli/*` | All CLI logic. |
| `agoras/commands/*` | `agoras/cli/commands/*` | Command implementations. |

## 3. Code Separation Strategy

### Current State

- **Released Version**: `v1.1.3` (monolithic, published and tagged on PyPI)
- **Development Branch**: `develop` (working on v2.0 features)
- **Package Split Status**: Final feature to be added before v2.0 release
- **Users**: Currently on v1.1.3, expect stable API and import paths

### Strategy: Package Split as Final v2.0 Feature

The package split is the last architectural change before v2.0 release. All other v2.0 features are already implemented on the `develop` branch.

#### Branch Strategy

- **Current Branch**: `develop` (all work happens here)
- **v1.1.3**: Already tagged and published (no further changes needed)
- **v1.x Maintenance**: If critical patches needed, cherry-pick to a `v1-maintenance` branch

#### Versioning Strategy

- **v1.1.3**: Already published (monolithic, stable on PyPI)
- **v2.0.0-alpha**: Package split complete, internal testing (TestPyPI)
- **v2.0.0**: Production release with all v2.0 features + package split (PyPI)

#### PyPI Strategy

- `agoras==1.1.3`: Available indefinitely (monolithic)
- `agoras==2.0.0`: New modular CLI package (depends on 4 sub-packages)
- Users must explicitly upgrade: `pip install agoras>=2.0.0`
- Breaking changes documented prominently in release notes

#### Migration Path for Users

1. **Current**: Users run `pip install agoras` → gets v1.1.3
2. **After v2.0 release**: Users must explicitly upgrade → `pip install "agoras>=2.0.0"`
3. **Import Changes**: All import paths change due to package split
4. **v1.1.3 Support**: Remains on PyPI for users not ready to migrate

#### Documentation Requirements

- `MIGRATION.rst`: Step-by-step guide from v1 → v2 with import path changes
- `CHANGELOG.md`: Comprehensive list of all v2.0 features + breaking changes
- `README.rst`: Updated for new modular architecture
- Update docs site with v1 vs v2 comparison and migration guide

### Implementation Timeline

This package split happens on the `develop` branch as the final v2.0 feature:

1. **Weeks 1-4**: Execute package split (detailed in Implementation Plan below)

2. **Week 5 (Alpha Release)**:
   - Complete package split and integration testing
   - Tag `v2.0.0-alpha` on `develop`
   - Publish to TestPyPI for testing
   - Internal testing and feedback collection

3. **Week 6-7 (Stabilization)**:
   - Fix issues found during alpha testing
   - Final integration tests across all packages
   - Documentation finalization

4. **Week 8 (Production Release)**:
   - Merge `develop` → `main`
   - Tag `v2.0.0` on `main`
   - Publish all 5 packages to PyPI
   - Announce v2.0 release with migration guide

### Breaking Changes to Document

| v1.x Import | v2.x Import | Notes |
| :--- | :--- | :--- |
| `from agoras.core import Facebook` | `from agoras.platforms.facebook import Facebook` | Platform wrappers moved |
| `from agoras.core.media import MediaFactory` | `from agoras.media import MediaFactory` | Media is now separate |
| `from agoras.core.feed import Feed` | `from agoras.core.feed import Feed` | Feed stays in core (works) |
| `from agoras.core.logger import setup_logger` | `from agoras.common.logger import setup_logger` | Logger moved to common |

## 4. Implementation Plan (Week-by-Week)

### Week 0: Pre-Migration Preparation

**Goal**: Document current state and prepare for package split.

**Note**: We're already on the `develop` branch with v2.0 features implemented.

1. **Day 1: Current State Documentation**
   - Document all current import paths (for MIGRATION.rst)
   - List all v2.0 features already implemented
   - Identify which modules depend on which

2. **Day 2: Communication & Planning**
   - Draft `MIGRATION.rst` skeleton (v1 → v2 import changes)
   - Update project roadmap/milestones for package split
   - Review and finalize the package split plan

3. **Day 3: Baseline Tests**
   - Document current test coverage
   - Document all current entry points and APIs

4. **Day 4-5: Repository Structure Preparation**
   - Create `packages/` directory structure in `develop`
   - Set up shared development tools (tox, nox, pre-commit)
   - Prepare CI/CD pipeline changes for multi-package builds

### Week 1: Foundation & Low-Level Components

**Goal**: Establish the monorepo structure and extract independent utilities.

1. **Day 1: Monorepo Setup**
    - Create top-level directory structure: `packages/common`, `packages/media`, `packages/core`, `packages/platforms`, `packages/cli`.
    - Initialize `git` handling (decide if using submodules or just folders).
    - Set up root-level `dev-requirements.txt` or toolchain (e.g., `tox`, `nox`) for running tests across all packages.

2. **Day 2: `agoras-common`**
    - Extract `agoras/core/utils.py` and `agoras/core/logger.py` to `packages/common/src/agoras/common/`.
    - Create `packages/common/setup.py`.
    - Write unit tests for `agoras-common` to ensure standalone functionality.

3. **Day 3: `agoras-media`**
    - Extract `agoras/core/media/` to `packages/media/src/agoras/media/`.
    - Update imports in media files to use `agoras.common`.
    - Add `agoras-common` as a dependency in `packages/media/setup.py`.

4. **Day 4-5: Verification & Testing**
    - Create a test environment installing both `agoras-common` and `agoras-media`.
    - Run existing media-related tests to verify nothing broke during extraction.

### Week 2: Core Logic & Interfaces

**Goal**: Define the abstract layer and migrate shared business logic.

1. **Day 1: `agoras-core` Interfaces**
    - Extract `agoras/core/base.py` (SocialNetwork interface) to `packages/core/src/agoras/core/interfaces.py`.
    - Extract `agoras/core/api/base.py` (BaseAPI) and all shared `agoras/core/api/auth/` files (base, storage, exceptions, callback_server) to `packages/core/src/agoras/core/`.

2. **Day 2: `agoras-core` Logic (Feed & Sheets)**
    - Move `agoras/core/feed/` and `agoras/core/sheet/` to `packages/core/src/agoras/core/`.
    - Refactor these modules to import from `agoras.common` and `agoras.media`.
    - Ensure strict dependency layering (Core -> Media -> Common).

3. **Day 3-4: `agoras-platforms` Setup**
    - Initialize `packages/platforms/src/agoras/platforms/`.
    - Move platform-specific files to their respective subdirectories (`facebook/`, `twitter/`, etc.).
    - **Refactor**: Update all imports to point to `agoras.core` for interfaces and base classes.

4. **Day 5: Platform Testing**
    - Verify that each platform implementation can still be instantiated and Mock-tested using the new structure.

### Week 3: CLI & Integration

**Goal**: Wire everything together and ensure the user experience remains unchanged.

1. **Day 1: `agoras-cli` Refactoring**
    - Move `agoras/cli/` to `packages/cli/src/agoras/cli/`.
    - Update `agoras/cli.py` entry point to import from the new package structure.
    - Update `setup.py` for CLI to depend on `agoras-platforms`.

2. **Day 2: Dependency Wiring**
    - Ensure `pip install .` in `packages/cli` correctly pulls in all 4 dependencies (`platforms`, `core`, `media`, `common`).
    - Fix any circular imports or namespace package issues that arise during integration.

3. **Day 3-5: End-to-End Testing**
    - Run the full test suite (`tox`).
    - Perform manual "smoke tests" for key commands (`post`, `schedule`, `authorize`).
    - Verify that `agoras --version` works and reports correctly.

### Week 3.5: Cleanup Phase (Monolithic Codebase Removal)

**Goal**: Remove the old monolithic codebase after migration is complete and tested.

**Prerequisites**: Week 3 complete, all tests passing, new structure verified working.

1. **Day 1: Prepare for Cleanup**
    - Document what will be removed in cleanup plan
    - Verify all functionality exists in new packages
    - Run final verification tests

2. **Day 2: Remove Old Source Files**
    - Remove `agoras/core/` directory (migrated to packages/core and packages/platforms)
    - Remove `agoras/cli/` directory (migrated to packages/cli)
    - Remove `agoras/commands/` directory (migrated to packages/cli/commands)
    - Remove old `agoras/cli.py` entry point (replaced by packages/cli/src/agoras/cli/main.py)
    - Keep `agoras/__init__.py` temporarily for version reference
    - Remove old Python test files from `tests/`: `tests/test_core_*.py` (migrated to package-specific tests)
    - Remove `tests/cli/` directory (migrated to packages/cli/tests)
    - **Keep** `tests/*.sh` integration scripts (will update in Day 4)

3. **Day 3: Update Root Configuration**
    - Update root `setup.py` to point to packages or remove if obsolete
    - Update root `requirements.txt` to reference package dependencies
    - Update `.gitignore` to exclude old build artifacts
    - Update `MANIFEST.in` for new structure
    - Remove old `.egg-info` directories

4. **Day 4: Update Integration Test Scripts**
    - Update `tests/*.sh` scripts to use new command structure
    - Change from `python3 -m agoras.cli` to `agoras` command
    - Update any old parameter names (e.g., `--twitter-consumer-key` → `--consumer-key`)
    - Verify scripts still work (if credentials available)
    - Document that these are E2E integration tests (separate from unit tests)
    - Keep scripts in root `tests/` directory for end-to-end testing

    **Scripts to Update**:
    - `tests/test.sh` - Master test runner
    - `tests/test-post.sh` - Post/video/like/share/delete tests
    - `tests/test-last-from-feed.sh` - RSS last item publishing
    - `tests/test-random-feed.sh` - RSS random item publishing
    - `tests/test-schedule.sh` - Google Sheets scheduling

5. **Day 5: Update Documentation References**
    - Update all documentation referencing old paths
    - Update import examples in docs
    - Update CLI_PARAMETERS.md if needed
    - Update CONTRIBUTING.rst with new package structure
    - Update any README references to old structure

6. **Day 6: Final Cleanup & Verification**
    - Remove any remaining monolithic artifacts
    - Verify no broken symlinks or references
    - Run full test suite one final time (packages/*/tests/)
    - Optionally test integration scripts: `tests/test.sh` (requires credentials)
    - Commit cleanup changes
    - Tag as pre-release: `v2.0.0-alpha` or `v2.0.0-rc1`

**Files/Directories to Remove**:

```
agoras/core/              → migrated to packages/core and packages/platforms
agoras/cli/               → migrated to packages/cli
agoras/commands/          → migrated to packages/cli/commands
agoras/cli.py             → migrated to packages/cli/src/agoras/cli/main.py
tests/cli/                → migrated to packages/cli/tests
tests/test_core_*.py      → migrated to packages/*/tests
```

**Files/Directories to Keep**:

```
tests/*.sh                → Integration/E2E tests (update command invocation)
tests/__init__.py         → May be needed for test discovery
```

**Files to Keep and Update**:

```
agoras/__init__.py        → Keep temporarily, may need for legacy compatibility
setup.py                  → Update to meta-package or remove
requirements.txt          → Update or replace with packages references
README.rst                → Update for v2.0 structure
tests/*.sh                → Update command invocation (see Day 4 above)
```

**Integration Test Scripts Purpose**:

The shell scripts in `tests/` are **end-to-end integration tests** that:

- Test actual API calls with real credentials (not mocks)
- Verify complete workflows: authorize → post → like → share → delete
- Test feed automation and scheduling features
- Run against live social media APIs
- Are separate from unit tests in `packages/*/tests/`

These should remain at the root level as they test the fully integrated CLI tool, not individual packages.

### Week 4: Release & Documentation

**Goal**: Polish, document, and publish.

1. **Day 1: CI/CD Pipeline Update**
    - Update GitHub Actions (or other CI) to build and test 5 separate packages.
    - Create a release workflow that publishes all 5 packages to PyPI (or TestPyPI first).
    - Remove references to old monolithic build process.

2. **Day 2: Documentation**
    - Update `README.rst` to explain the new modular structure.
    - Add "Advanced Installation" docs (e.g., "How to install only the Core").
    - Update Developer Guides (Contributing).
    - Finalize MIGRATION.rst with complete v1→v2 guide.

## 5. Example `setup.py` Configuration (Namespace Packages)

For `agoras-common`:

```python
# packages/common/setup.py
setup(
    name='agoras-common',
    packages=['agoras.common'],
    package_dir={'': 'src'},
    # ...
)
```

For `agoras-core`:

```python
# packages/core/setup.py
setup(
    name='agoras-core',
    packages=['agoras.core'],
    package_dir={'': 'src'},
    install_requires=[
        'agoras-common>=2.0.0',
        'agoras-media>=2.0.0'
    ],
    # ...
)
```

## 6. Potential Pitfalls & Mitigations

- **Circular Imports**: Strict layering prevents this. If `core` needs something from `platforms` (unlikely, but possible via factories), use dependency injection or dynamic loading.
- **Namespace Collisions**: Ensure every package uses the same `src/agoras` directory structure so they merge correctly when installed.
- **Development Friction**: Use `pip install -e .` for all 5 packages in your virtualenv during development to edit them simultaneously.
