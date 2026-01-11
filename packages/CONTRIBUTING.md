# Contributing to Agoras Packages

This guide explains how to develop and contribute to the Agoras v2.0 monorepo structure.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git
- pip

### Initial Setup

1. **Clone the repository**:
```bash
git clone https://github.com/LuisAlejandro/agoras.git
cd agoras
git checkout develop
```

2. **Create a virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install all packages in editable mode** (in dependency order):
```bash
cd packages

# Install in dependency order
pip install -e common/
pip install -e media/
pip install -e core/
pip install -e platforms/
pip install -e cli/

# Install development dependencies
pip install -r dev-requirements.txt
```

## Development Workflow

### Making Changes

1. **Identify the correct package** for your changes:
   - `common/`: Utilities, logging, version info
   - `media/`: Image/video processing
   - `core/`: Interfaces, Feed, Sheet, Base classes
   - `platforms/`: Platform-specific implementations
   - `cli/`: Command-line interface

2. **Make your changes** in the appropriate package's `src/agoras/<package>/` directory

3. **Update tests** in the package's `tests/` directory

### Running Tests

#### Test a Single Package

```bash
cd packages/<package>
pytest tests/ -v
```

#### Test All Packages

```bash
cd packages
tox
```

#### Test with Coverage

```bash
cd packages/<package>
pytest tests/ -v --cov=agoras --cov-report=html
# Open htmlcov/index.html to view coverage report
```

#### Run Integration Tests

```bash
cd packages
pytest cli/tests/ -v -k integration
```

### Building Packages

Build a single package:

```bash
cd packages/<package>
python setup.py sdist bdist_wheel
```

Build all packages:

```bash
cd packages
for pkg in common media core platforms cli; do
    cd $pkg
    python setup.py sdist bdist_wheel
    cd ..
done
```

### Testing Package Installation

Test that packages install correctly:

```bash
# Create a fresh virtualenv
python3 -m venv test-venv
source test-venv/bin/activate

# Install in order
pip install packages/common/dist/agoras_common-2.0.0-py3-none-any.whl
pip install packages/media/dist/agoras_media-2.0.0-py3-none-any.whl
pip install packages/core/dist/agoras_core-2.0.0-py3-none-any.whl
pip install packages/platforms/dist/agoras_platforms-2.0.0-py3-none-any.whl
pip install packages/cli/dist/agoras-2.0.0-py3-none-any.whl

# Test CLI
agoras --version
agoras --help
```

## Code Style

### Linting

```bash
cd packages
flake8 common/src/agoras
flake8 media/src/agoras
flake8 core/src/agoras
flake8 platforms/src/agoras
flake8 cli/src/agoras
```

### Formatting

```bash
autopep8 --in-place --recursive packages/*/src/agoras
```

## Package Dependencies

Understanding the dependency chain is critical:

```
cli → platforms → core → media → common
                  ↓
                feed/sheet
```

**Rules**:
- Lower-level packages CANNOT import from higher-level packages
- Each package only imports from its direct dependencies
- No circular dependencies allowed

## Common Tasks

### Adding a New Platform

1. Create files in `packages/platforms/src/agoras/platforms/<platform>/`:
   - `__init__.py`
   - `wrapper.py` (SocialNetwork implementation)
   - `api.py` (API manager)
   - `client.py` (HTTP client)
   - `auth.py` (Auth manager)

2. Add platform SDK to `packages/platforms/requirements.txt`

3. Create tests in `packages/platforms/tests/test_<platform>.py`

4. Register platform in CLI

### Adding a New Utility

1. Add function to `packages/common/src/agoras/common/utils.py`
2. Write tests in `packages/common/tests/test_utils.py`
3. Update documentation

### Updating Dependencies

1. Update requirements.txt in the appropriate package
2. Rebuild the package
3. Test that installation works

## Troubleshooting

### Import Errors

If you get import errors:
1. Ensure all packages are installed in editable mode
2. Check that you're in the correct virtual environment
3. Verify dependency installation order

### Test Failures

If tests fail after changes:
1. Run tests for the specific package you changed
2. Run integration tests
3. Check import paths (v2.0 uses new namespaces)

### Namespace Package Issues

If packages don't merge correctly:
1. Ensure NO `__init__.py` in `src/agoras/` directory
2. Ensure YES `__init__.py` in `src/agoras/<package>/` directory
3. Use `find_namespace_packages(where='src')` in setup.py

## See Also

- [Package Split Plan](../.cursor/plans/package-split/PACKAGE_SPLIT_PLAN.md)
- [Migration Guide](../MIGRATION.md)
- [Main Contributing Guide](../CONTRIBUTING.rst)
