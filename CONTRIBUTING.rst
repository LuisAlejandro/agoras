.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/LuisAlejandro/agoras/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "feature"
is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

agoras could always use more documentation, whether as part of the
official agoras docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/LuisAlejandro/agoras/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `agoras` for local development.

1. Fork the `agoras` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/agoras.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ mkvirtualenv agoras
    $ cd agoras/
    $ pip install -e packages/common -e packages/media -e packages/core -e packages/platforms -e packages/cli

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the tests, including testing other Python versions with tox::

    $ pip install -r requirements-dev.txt  # Install development dependencies
    $ tox -e lint
    $ tox -e all

   Development dependencies are managed in ``requirements-dev.txt`` and include:
   pytest, coverage, flake8, pydocstyle, tox, and build tools.

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Monorepo Development (v2.0)
----------------------------

Starting with v2.0, Agoras uses a monorepo structure with 5 separate packages.
If you're working on v2.0 code, follow this comprehensive guide.

Development Setup
~~~~~~~~~~~~~~~~~

Prerequisites:

* Python 3.9 or higher
* Git
* pip

Initial Setup:

1. Clone the repository (if you haven't already)::

    $ git clone https://github.com/LuisAlejandro/agoras.git
    $ cd agoras
    $ git checkout develop

2. Create a virtual environment::

    $ python3 -m venv venv
    $ source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install all packages in editable mode (in dependency order)::

    # Install in dependency order
    $ pip install -e packages/common/
    $ pip install -e packages/media/
    $ pip install -e packages/core/
    $ pip install -e packages/platforms/
    $ pip install -e packages/cli/

    # Install development dependencies
    $ pip install -r requirements-dev.txt

4. Verify installation::

    $ python -c "from agoras.common.version import __version__; print(__version__)"
    $ python -c "from agoras.cli.main import commandline; print('CLI imported successfully')"
    $ agoras --version
    $ agoras --help

Package Structure
~~~~~~~~~~~~~~~~~

Identify the correct package for your changes::

    packages/
    ├── common/     # Utilities, logging, version info
    ├── media/      # Image/video processing
    ├── core/       # Interfaces, Feed, Sheet, Base classes
    ├── platforms/  # Platform-specific implementations
    └── cli/        # Command-line interface

Make your changes in the appropriate package's ``src/agoras/<package>/`` directory
and update tests in the package's ``tests/`` directory.

**Namespace Packages**: Agoras v2.0 uses Python namespace packages. All packages share
the ``agoras.*`` namespace, allowing imports like ``from agoras.common import ...``
and ``from agoras.platforms import ...``. Each package's code lives in
``packages/<package>/src/agoras/<package>/``, and when installed, they merge into
a single ``agoras`` namespace.

Package Dependencies
~~~~~~~~~~~~~~~~~~~~

Understanding the dependency chain is critical::

    cli → platforms → core → media → common
                      ↓
                    feed/sheet

**Dependency Rules**:

* Lower-level packages CANNOT import from higher-level packages
* Each package only imports from its direct dependencies
* No circular dependencies allowed

**Examples**:

✅ **Correct**: ``agoras.core`` can import from ``agoras.common`` and ``agoras.media``

✅ **Correct**: ``agoras.platforms`` can import from ``agoras.core``

❌ **Wrong**: ``agoras.common`` cannot import from ``agoras.core`` (circular dependency)

❌ **Wrong**: ``agoras.media`` cannot import from ``agoras.platforms`` (skips dependency chain)

**Verifying Dependencies**:

To check if your imports are correct, run::

    $ python -c "from agoras.<package> import <module>"

If you get import errors, check that:
1. The package you're importing from is installed
2. You're following the dependency chain
3. You're not creating circular dependencies

Running Tests
~~~~~~~~~~~~~

Test a single package::

    $ cd packages/<package>
    $ pytest tests/ -v

Test a specific package with tox::

    $ tox -e py39-common    # Test common package on Python 3.9
    $ tox -e py310-media     # Test media package on Python 3.10
    $ tox -e py311-core      # Test core package on Python 3.11
    $ tox -e py312-platforms # Test platforms package on Python 3.12
    $ tox -e py39-cli        # Test CLI package on Python 3.9

Test all packages with tox::

    $ tox                    # Tests all packages on all Python versions (3.9, 3.10, 3.11, 3.12)

Test all packages together (integration)::

    $ tox -e all             # Installs all packages and runs all tests

Test with coverage::

    $ cd packages/<package>
    $ pytest tests/ -v --cov=agoras --cov-report=html
    # Open htmlcov/index.html to view coverage report

    # Or use tox for aggregated coverage:
    $ tox -e coverage        # Aggregates coverage across all packages

Run integration tests::

    $ pytest packages/cli/tests/ -v -k integration

Run linting::

    $ tox -e lint            # Lints all packages

Testing Best Practices
~~~~~~~~~~~~~~~~~~~~~~

1. **Run tests before committing**: Always run tests for the package you modified
2. **Test dependencies**: If you change a lower-level package, test all dependent packages
3. **Integration tests**: Run integration tests when making cross-package changes
4. **Coverage**: Aim to maintain or improve test coverage
5. **Python versions**: Ensure tests pass on all supported Python versions (3.9-3.12)

Building Packages
~~~~~~~~~~~~~~~~~

Build a single package::

    $ cd packages/<package>
    $ python -m build

Build all packages::

    $ for pkg in common media core platforms cli; do
          cd packages/$pkg
          python -m build
          cd ../..
      done

Release Process (v2.0)
~~~~~~~~~~~~~~~~~~~~~~~

Agoras v2.0 uses a multi-package release process. All 5 packages must be released in dependency order.

Prerequisites
-------------

* Clean git working directory
* All tests passing
* All packages built successfully
* GitHub release created (triggers automated publishing)

Release Steps
-------------

1. **Version Bumping**: All packages are versioned together (e.g., 2.0.0)

   The version is managed in ``packages/common/src/agoras/common/version.py``
   and all packages reference this version.

2. **Create Release**: Use the release script::

    $ ./scripts/release.sh [major|minor|patch] [Release Name]

   This script:
   * Bumps version in all packages
   * Creates a git tag
   * Creates a GitHub release
   * Triggers GitHub Actions workflow

3. **Automated Publishing**: GitHub Actions automatically:

   * Builds all 5 packages in parallel
   * Publishes to PyPI in dependency order:
     1. agoras-common
     2. agoras-media (waits for common)
     3. agoras-core (waits for media)
     4. agoras-platforms (waits for core)
     5. agoras (CLI) (waits for platforms)
   * Uploads build artifacts to GitHub release

4. **Verification**: After release, verify packages are available::

    $ pip install agoras-common==2.0.0
    $ pip install agoras-media==2.0.0
    $ pip install agoras-core==2.0.0
    $ pip install agoras-platforms==2.0.0
    $ pip install agoras==2.0.0

Release Workflow
----------------

The release process follows this workflow:

1. Developer runs ``./scripts/release.sh patch "Bug Fix Release"``
2. Script bumps versions, creates tag, creates GitHub release
3. GitHub Actions workflow triggers on release creation
4. Workflow builds all packages in parallel
5. Workflow publishes packages to PyPI sequentially (with waits between)
6. Packages become available on PyPI

Hotfix Process
--------------

For urgent fixes, use the hotfix script::

    $ ./scripts/hotfix.sh [major|minor|patch] [Hotfix Name]

This follows the same process but creates a hotfix branch and merges to both develop and master.

Manual Release (Not Recommended)
---------------------------------

If you need to release manually (not recommended):

1. Update version in ``packages/common/src/agoras/common/version.py``
2. Build all packages::

    $ for pkg in common media core platforms cli; do
          cd packages/$pkg
          python -m build
          cd ../..
      done

3. Publish to PyPI in order::

    $ twine upload packages/common/dist/*
    # Wait 30 seconds
    $ twine upload packages/media/dist/*
    # Wait 30 seconds
    $ twine upload packages/core/dist/*
    # Wait 30 seconds
    $ twine upload packages/platforms/dist/*
    # Wait 30 seconds
    $ twine upload packages/cli/dist/*

Testing Package Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Test that packages install correctly::

    # Create a fresh virtualenv
    $ python3 -m venv test-venv
    $ source test-venv/bin/activate

    # Install in order
    $ pip install packages/common/dist/agoras_common-2.0.0-py3-none-any.whl
    $ pip install packages/media/dist/agoras_media-2.0.0-py3-none-any.whl
    $ pip install packages/core/dist/agoras_core-2.0.0-py3-none-any.whl
    $ pip install packages/platforms/dist/agoras_platforms-2.0.0-py3-none-any.whl
    $ pip install packages/cli/dist/agoras-2.0.0-py3-none-any.whl

    # Test CLI
    $ agoras --version
    $ agoras --help

Code Style
~~~~~~~~~~

Run linting::

    $ flake8 packages/common/src/agoras
    $ flake8 packages/media/src/agoras
    $ flake8 packages/core/src/agoras
    $ flake8 packages/platforms/src/agoras
    $ flake8 packages/cli/src/agoras

Format code::

    $ autopep8 --in-place --recursive packages/*/src/agoras

Common Development Workflows
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Making Changes to a Single Package
----------------------------------

1. Navigate to package directory::

    $ cd packages/<package>

2. Make your changes in ``src/agoras/<package>/``

3. Update tests in ``tests/``

4. Run tests::

    $ pytest tests/ -v

5. Run linting::

    $ flake8 src/agoras

6. Commit changes::

    $ git add .
    $ git commit -m "Description of changes"

Making Changes Across Multiple Packages
----------------------------------------

1. Install all packages in editable mode (if not already)::

    $ pip install -e packages/common/
    $ pip install -e packages/media/
    $ pip install -e packages/core/
    $ pip install -e packages/platforms/
    $ pip install -e packages/cli/

2. Make changes in dependency order (common → media → core → platforms → cli)

3. Test each package as you go::

    $ cd packages/common && pytest tests/ -v
    $ cd ../media && pytest tests/ -v
    # etc.

4. Run integration tests::

    $ tox -e all

5. Run full test suite::

    $ tox

Common Tasks
~~~~~~~~~~~~

Adding a New Platform:

1. Create files in ``packages/platforms/src/agoras/platforms/<platform>/``:

   * ``__init__.py``
   * ``wrapper.py`` (SocialNetwork implementation)
   * ``api.py`` (API manager)
   * ``client.py`` (HTTP client)
   * ``auth.py`` (Auth manager)

2. Add platform SDK to ``packages/platforms/requirements.txt``

3. Create tests in ``packages/platforms/tests/test_<platform>.py``

4. Register platform in CLI

Adding a New Utility:

1. Add function to ``packages/common/src/agoras/common/utils.py``
2. Write tests in ``packages/common/tests/test_utils.py``
3. Update documentation

Updating Dependencies:

1. Update requirements.txt in the appropriate package
2. Rebuild the package
3. Test that installation works

Troubleshooting
~~~~~~~~~~~~~~~

Import Errors:

If you get import errors:

1. Ensure all packages are installed in editable mode
2. Check that you're in the correct virtual environment
3. Verify dependency installation order

Test Failures:

If tests fail after changes:

1. Run tests for the specific package you changed
2. Run integration tests
3. Check import paths (v2.0 uses new namespaces)

Namespace Package Issues:

If packages don't merge correctly:

1. Ensure NO ``__init__.py`` in ``src/agoras/`` directory
2. Ensure YES ``__init__.py`` in ``src/agoras/<package>/`` directory
3. Use ``find_namespace_packages(where='src')`` in setup.py

CI/CD Expectations
~~~~~~~~~~~~~~~~~~

When submitting pull requests:

* All 5 packages must pass their individual test suites
* Integration tests must pass (CLI with all packages)
* Linting must pass for all packages (flake8, pydocstyle)
* Coverage reports are aggregated across packages
* GitHub Actions will run tests on Python 3.9, 3.10, 3.11, 3.12

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. Check https://github.com/LuisAlejandro/agoras/actions
   and make sure that the tests pass for all supported Python versions.

Tips
----

To run a subset of tests::


    $ python -m unittest tests.test_core_logger
    $ python -m unittest tests.test_core_utils
