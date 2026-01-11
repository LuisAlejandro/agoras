# Comprehensive Test Coverage Increase Plan

This plan outlines the strategy to increase the code coverage of all packages in `packages/` to at least 60%.

## Current State Assessment

- **Packages:** `cli`, `common`, `core`, `media`, `platforms`.
- **Infrastructure:** `tox` and `pytest` are configured.
- **Coverage Gap:**
    - `platforms` package has minimal tests (only instantiation/inheritance).
    - `core` and other packages have some tests but likely need reinforcement to reach 60%.
    - `cli` tests focus on argument parsing, not integration.

## Goal
- Achieve >60% code coverage for each package.
- Prioritize unit tests over integration tests for speed and stability.
- Mock external dependencies (API calls) effectively.

---

## Schedule

### Week 1: Foundation & Common Utilities

**Objective:** Establish baseline coverage and secure the foundational packages (`common` and `media`).

*   **Day 1: Setup & Baseline**
    *   Run full coverage report to get exact current numbers: `tox -e coverage`.
    *   Identify "low hanging fruit" (untested utility functions).
    *   Fix any immediate configuration issues with coverage reporting.
*   **Day 2: Common Package - Utils & Logger**
    *   Add tests for `agoras.common.utils`.
    *   Add tests for `agoras.common.logger`.
    *   Goal: >80% coverage for `common`.
*   **Day 3: Media Package - Base & Factory**
    *   Test `agoras.media.base` classes.
    *   Test `agoras.media.factory` logic.
*   **Day 4: Media Package - Image & Video**
    *   Add unit tests for `agoras.media.image` (mocking file operations if needed).
    *   Add unit tests for `agoras.media.video`.
*   **Day 5: Review & Refine**
    *   Run coverage for `common` and `media`.
    *   Refactor tests for better readability.

### Week 2: Core Package (Business Logic)

**Objective:** Cover the core interfaces and shared logic.

*   **Day 1: Core - API Base & Interfaces**
    *   Test `agoras.core.api_base`.
    *   Test `agoras.core.interfaces` (ensure abstract methods are enforced).
*   **Day 2: Core - Feed Manager**
    *   Test `agoras.core.feed.manager`.
    *   Test `agoras.core.feed.item` and `feed.py`.
*   **Day 3: Core - Sheet Manager**
    *   Test `agoras.core.sheet` (parsing logic, row handling).
    *   Mock CSV/Excel inputs.
*   **Day 4: Core - Auth (Storage)**
    *   Test `agoras.core.auth.storage` (saving/loading tokens).
    *   Test `agoras.core.auth.exceptions`.
*   **Day 5: Core - Auth (Callback)**
    *   Test `agoras.core.auth.callback_server`.
    *   Mock HTTP requests for callback handling.

### Week 3: Platforms (The Big Chunk - Part 1)

**Objective:** Start testing the platform-specific implementations. Heavy mocking required.

*   **Day 1: Platform Testing Infrastructure**
    *   Create robust mocks for network requests (using `responses` or `unittest.mock`).
    *   Create a base test class for Platforms to reduce boilerplate.
*   **Day 2: Facebook**
    *   Test `agoras.platforms.facebook`.
    *   Cover: Auth flow, Post (text/media), Error handling.
*   **Day 3: Instagram**
    *   Test `agoras.platforms.instagram`.
    *   Cover: Auth flow, Post (media requirements), Error handling.
*   **Day 4: LinkedIn**
    *   Test `agoras.platforms.linkedin`.
    *   Cover: Auth flow, Post, Error handling.
*   **Day 5: Catch-up & Refactor**
    *   Ensure shared mocking patterns are working.

### Week 4: Platforms (Part 2)

**Objective:** Continue through the platform list.

*   **Day 1: Discord**
    *   Test `agoras.platforms.discord`.
    *   Mock Discord API interactions.
*   **Day 2: Telegram**
    *   Test `agoras.platforms.telegram`.
    *   Mock Bot API interactions.
*   **Day 3: WhatsApp**
    *   Test `agoras.platforms.whatsapp`.
    *   Mock Meta Business API.
*   **Day 4: X (Twitter)**
    *   Test `agoras.platforms.x`.
    *   Mock OAuth1/2 flows.
*   **Day 5: Threads**
    *   Test `agoras.platforms.threads`.

### Week 5: Platforms (Final) & CLI

**Objective:** Finish platforms and start CLI coverage.

*   **Day 1: TikTok**
    *   Test `agoras.platforms.tiktok`.
*   **Day 2: YouTube**
    *   Test `agoras.platforms.youtube`.
*   **Day 3: CLI - Registry & Validator**
    *   Test `agoras.cli.registry`.
    *   Test `agoras.cli.validator`.
*   **Day 4: CLI - Converter & Legacy**
    *   Test `agoras.cli.converter`.
    *   Test `agoras.cli.legacy` (if applicable).
*   **Day 5: CLI - Commands**
    *   Test `agoras.cli.commands.publish` (mocking the actual platform calls).
    *   Verify argument parsing logic thoroughly.

### Week 6: Integration & Finalization

**Objective:** Ensure everything works together and hit the 60% target.

*   **Day 1: Cross-Package Integration**
    *   Write tests that simulate the flow from CLI -> Core -> Platform (mocked).
*   **Day 2: Edge Cases**
    *   Test error propagation (e.g., Platform error -> Core -> CLI -> User output).
*   **Day 3: Coverage Gap Analysis**
    *   Run full coverage report.
    *   Identify specific files that are still under 60%.
*   **Day 4: Targeted Filling**
    *   Write specific tests for the remaining low-coverage files.
*   **Day 5: Final Polish**
    *   Standardize test docstrings.
    *   Ensure linting passes on all new tests.

## Notes

- **Mocking:** Since `platforms` interact with external APIs, 90% of the tests there will rely on mocking `requests` or the specific SDK clients.
- **Independence:** Tests should be independent. Avoid shared state.
- **Tools:** Use `tox` to run tests locally in isolated environments.
