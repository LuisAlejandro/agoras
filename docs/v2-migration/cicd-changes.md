# CI/CD Pipeline Changes for v2.0

This document outlines the changes needed for GitHub Actions workflows to support the multi-package architecture.

## Current Workflow (v1.x)

**File**: `.github/workflows/push.yml`

**Structure**:
1. Single build job with Python version matrix (3.9, 3.10, 3.11, 3.12)
2. Install dependencies from `requirements.txt` and `requirements-dev.txt`
3. Run `tox` for testing
4. Upload coverage to Coveralls
5. Aggregate coverage results

**Limitations**:
- Tests all code as a monolithic package
- Cannot test packages independently
- Single publish workflow

## New Workflow (v2.0)

**File**: `.github/workflows/push-v2.yml.draft`

### Key Changes

#### 1. Multi-Package Testing

**Job**: `test-packages`
- Matrix: Python versions × Packages (3.9-3.12 × 5 packages)
- Total: 20 test jobs (4 Python versions × 5 packages)
- Each package tested independently

**Installation Order** (critical):
```bash
1. agoras-common (no dependencies)
2. agoras-media (depends on common)
3. agoras-core (depends on common, media)
4. agoras-platforms (depends on core)
5. agoras-cli (depends on platforms)
```

#### 2. Integration Testing

**Job**: `test-integration`
- Tests all packages together
- Verifies inter-package compatibility
- Tests CLI entry point

#### 3. Linting

**Job**: `lint`
- Lints all 5 packages
- Runs on Python 3.11
- Uses flake8 and pydocstyle

#### 4. Coverage Aggregation

**Job**: `finish-coverage`
- Waits for all `test-packages` jobs
- Aggregates coverage from all packages
- Uploads to Coveralls

#### 5. Package Building

**Job**: `build-packages`
- Runs only on `master` branch
- Builds all 5 packages
- Uploads build artifacts
- Matrix: 5 packages

#### 6. PyPI Publishing

**Job**: `publish-to-pypi`
- Triggered by version tags (e.g., `v2.0.0`)
- Publishes packages in dependency order:
  1. agoras-common
  2. agoras-media
  3. agoras-core
  4. agoras-platforms
  5. agoras (CLI)
- Uses PyPI trusted publishing (OIDC)

#### 7. GitHub Release

**Job**: `create-release`
- Creates GitHub release
- Links to CHANGELOG and MIGRATION.md
- Runs after successful PyPI publish

## Workflow Comparison

| Feature | v1.x Workflow | v2.0 Workflow |
|---------|---------------|---------------|
| Test Jobs | 4 (Python versions) | 20 (versions × packages) |
| Package Tests | Monolithic | Independent per package |
| Integration Tests | Implicit | Explicit job |
| Build Artifacts | 1 package | 5 packages |
| PyPI Publish | 1 package | 5 packages (ordered) |
| Coverage | Single report | Aggregated from 5 packages |

## Migration Steps

### Phase 1: Testing (Week 1-3)

1. **Keep current workflow active** (`.github/workflows/push.yml`)
2. **Use draft workflow for testing** (`.github/workflows/push-v2.yml.draft`)
3. **Run both workflows in parallel** during migration

### Phase 2: Transition (Week 4)

1. **Rename workflows**:
   - `push.yml` → `push-v1.yml.disabled`
   - `push-v2.yml.draft` → `push.yml`
2. **Update branch triggers** if needed
3. **Test on develop branch** before merging to master

### Phase 3: Production (Week 5+)

1. **Activate new workflow** on master branch
2. **First release**: Tag `v2.0.0-alpha` to trigger publish
3. **Monitor**: Check all 5 packages publish successfully
4. **Cleanup**: Remove old workflow after successful v2.0.0 release

## New Workflow Features

### Dependency Order Enforcement

The workflow ensures packages are installed in the correct order:

```yaml
- name: Install dependencies in order
  run: |
    cd packages
    pip install -e common/
    pip install -e media/
    pip install -e core/
    pip install -e platforms/
    pip install -e cli/
```

### Per-Package Coverage

Each package generates its own coverage report:

```yaml
- name: Run tests for ${{ matrix.package }}
  run: |
    cd packages/${{ matrix.package }}
    pytest tests/ -v --cov=agoras --cov-report=lcov
```

### Parallel Testing

All packages test in parallel across Python versions:
- 5 packages × 4 Python versions = 20 parallel jobs
- Faster CI/CD execution
- Early failure detection per package

### Artifact Management

Build artifacts are uploaded per package:

```yaml
- name: Upload artifacts
  uses: actions/upload-artifact@v4
  with:
    name: dist-${{ matrix.package }}
    path: packages/${{ matrix.package }}/dist/*
```

### PyPI Publishing Order

Critical: Packages must be published in dependency order to avoid installation failures:

```yaml
# 1. Common (no dependencies)
- name: Publish agoras-common
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    packages-dir: dist/dist-common/

# 2. Media (depends on common)
- name: Publish agoras-media
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    packages-dir: dist/dist-media/

# ... and so on
```

## Testing Strategy

### Unit Tests (Per Package)

Each package tests its own modules:
- `packages/common/tests/` → Tests for utils, logger
- `packages/media/tests/` → Tests for image, video processing
- `packages/core/tests/` → Tests for interfaces, feed, sheet
- `packages/platforms/tests/` → Tests for platform implementations
- `packages/cli/tests/` → Tests for CLI commands

### Integration Tests

The `test-integration` job tests cross-package functionality:
- CLI commands that use platforms
- Platforms that use core interfaces
- End-to-end workflows

### Coverage Goals

| Package | Target Coverage | Priority |
|---------|----------------|----------|
| agoras-common | 80%+ | High (utilities should be well-tested) |
| agoras-media | 60%+ | Medium (add tests during split) |
| agoras-core | 70%+ | High (critical interfaces) |
| agoras-platforms | 40%+ | Medium (integration-focused) |
| agoras-cli | 60%+ | High (user-facing) |

## Secrets and Configuration

### Required Secrets

Same as v1.x:
- `GITHUB_TOKEN`: Provided by GitHub Actions
- `PYPI_API_TOKEN`: For PyPI publishing (if not using OIDC)

### Environment Configuration

For PyPI publishing with OIDC (recommended):
- Configure PyPI trusted publisher
- Add `id-token: write` permission
- No API token needed

## Rollback Plan

If the new workflow fails:

1. **Immediate**: Re-enable `push-v1.yml`
2. **Investigate**: Check logs for specific package failures
3. **Fix**: Update package structure or workflow
4. **Retry**: Test on develop branch before master

## Performance Considerations

### Build Time

- **v1.x**: ~5-10 minutes (4 Python versions)
- **v2.0**: ~10-15 minutes (20 parallel jobs + integration)
- **Parallelization**: Jobs run concurrently, so wall-clock time similar

### Resource Usage

- **GitHub Actions minutes**: ~5x increase (20 jobs vs 4)
- **Mitigation**: Use caching, optimize test execution

### Optimization Strategies

1. **Caching**:
   - Cache pip dependencies
   - Cache built packages between jobs

2. **Conditional Jobs**:
   - Run full matrix only on master/develop
   - Run subset on feature branches

3. **Fast Fail**:
   - Stop on first failure in critical jobs
   - Continue on error for non-critical tests

## Next Steps

1. **Week 1-3**: Use draft workflow for testing during migration
2. **Week 4**: Activate new workflow on develop branch
3. **Week 5**: Test alpha release (v2.0.0-alpha)
4. **Week 8**: Production release (v2.0.0) with full workflow active

## References

- Current workflow: [.github/workflows/push.yml](../../.github/workflows/push.yml)
- Draft workflow: [.github/workflows/push-v2.yml.draft](../../.github/workflows/push-v2.yml.draft)
- Package structure: [packages/README.md](../../packages/README.md)
