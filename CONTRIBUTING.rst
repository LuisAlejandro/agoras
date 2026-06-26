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

Improve Documentation
~~~~~~~~~~~~~~~~~~~

agoras could always use more documentation, whether as part of the
official agoras docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/LuisAlejandro/agoras/issues.

Suggest Features
~~~~~~~~~~~~~~~~

The best way to suggest a feature is to file an issue at https://github.com/LuisAlejandro/agoras/issues.

If you are proposing a feature:

* Explain the problem you are trying to solve.
* Describe the behavior you want and any alternatives you considered.
* Keep the scope as narrow as possible, to make it easier to implement.

Local Development
-----------------

Ready to contribute? Set up ``agoras`` for local development.

1. Fork the ``agoras`` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/agoras.git
    $ cd agoras
    $ git checkout develop

3. Copy environment placeholders when you need credentials for integration tests::

    $ cp .env.example .env

4. Start the Docker development environment::

    $ make image
    $ make start
    $ make console    # optional interactive shell

   Alternatively, create a host virtualenv with ``make virtualenv`` and activate ``./virtualenv/bin/activate``.

5. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Quality Checks
--------------

Prefer Docker-backed ``make`` targets when developing with containers::

    $ make lint
    $ make format
    $ make test

Or run tox directly on the host::

    $ pip install -r requirements-dev.txt
    $ tox -e lint
    $ tox -e format
    $ tox -e coverage
    $ tox -e all

Development dependencies are managed in ``requirements-dev.txt`` and include
pytest, coverage, Ruff, Pyright, pydocstyle, bandit, tox, and build tools.

If you develop with Docker and ``requirements-dev.txt`` changes after a pull,
rebuild the image so the container picks up new tools (``make start`` alone does
not rebuild an existing image)::

    $ make image

Monorepo Development (v2.0)
----------------------------

Starting with v2.0, Agoras uses a monorepo structure with 5 separate packages.
If you're working on v2.0 code, follow this comprehensive guide.

Development Setup
~~~~~~~~~~~~~~~~~

Prerequisites:

* Python 3.10 or higher
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

    $ tox -e py310-media     # Test media package on Python 3.10
    $ tox -e py311-core      # Test core package on Python 3.11
    $ tox -e py312-platforms # Test platforms package on Python 3.12

Test all packages with tox::

    $ tox                    # Tests all packages on all Python versions (3.10, 3.11, 3.12, 3.13, 3.14)

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
5. **Python versions**: Ensure tests pass on all supported Python versions (3.10-3.14)

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

Lint and format production source under ``packages/*/src/agoras`` with tox
(Ruff format check, Ruff lint, pydocstyle, bandit, and Pyright)::

    $ tox -e lint
    $ tox -e format

Docker users can run the same checks via ``make lint`` and ``make format``.

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

    $ tox -e lint

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
* Linting must pass for all packages (``tox -e lint``: Ruff, pydocstyle, bandit, Pyright)
* Coverage reports are aggregated across packages
* GitHub Actions will run tests on Python 3.10, 3.11, 3.12, 3.13, 3.14

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. Check https://github.com/LuisAlejandro/agoras/actions
   and make sure that the tests pass for all supported Python versions.
4. Keep scope focused and link related issues when applicable.

Maintainer Notes
----------------

Releases, version bumps, PyPI publishing, and git tags are handled by maintainers.
Contributors do not need to publish packages or push release tags.

Tips
----

To run a subset of tests::


    $ python -m unittest tests.test_core_logger
    $ python -m unittest tests.test_core_utils
