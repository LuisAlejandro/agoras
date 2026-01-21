.. highlight:: shell

============
Installation
============

Agoras v2.0 is split into 5 separate PyPI packages. This guide covers all installation options.

Prerequisites
--------------

- Python 3.9 or higher
- pip (Python package installer)

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/

Full Installation (Recommended)
---------------------------------

For most users, installing the main CLI package is the easiest option. It automatically installs all dependencies:

.. code-block:: console

    $ pip install agoras

This installs all 5 packages:
- ``agoras-common``: Utilities, logging, shared constants
- ``agoras-media``: Image and video processing
- ``agoras-core``: Abstract interfaces, Feed, Sheet logic
- ``agoras-platforms``: Platform implementations
- ``agoras``: Command-line interface

Verify the installation:

.. code-block:: console

    $ agoras --version
    $ agoras --help

Selective Package Installation
-------------------------------

If you only need specific functionality, you can install individual packages. Packages automatically install their dependencies.

Installing Individual Packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**agoras-common** (Foundation Package)
  Minimal package with utilities and logging only:

  .. code-block:: console

      $ pip install agoras-common

  Use case: Standalone utilities, logging configuration, version information.

**agoras-media** (Media Processing)
  Includes common + media processing:

  .. code-block:: console

      $ pip install agoras-media

  Use case: Image and video processing without social network features.

**agoras-core** (Business Logic)
  Includes common + media + core interfaces:

  .. code-block:: console

      $ pip install agoras-core

  Use case: Building custom platform integrations, using Feed/Sheet automation without platform implementations.

**agoras-platforms** (Platform Implementations)
  Includes all above + platform implementations:

  .. code-block:: console

      $ pip install agoras-platforms

  Use case: Python integrations using platform APIs without CLI tool.

**agoras** (CLI Tool)
  Full installation including CLI:

  .. code-block:: console

      $ pip install agoras

  Use case: Command-line automation (most common use case).

Package Dependency Graph
~~~~~~~~~~~~~~~~~~~~~~~~

The packages follow a layered dependency structure:

.. code-block:: text

   agoras (CLI)
   └── agoras-platforms
       └── agoras-core
           ├── agoras-media
           └── agoras-common

When you install a package, all its dependencies are automatically installed.

Development Installation
-----------------------

For development or contributing to Agoras, install from source in the monorepo structure.

Prerequisites
~~~~~~~~~~~~~

- Git
- Python 3.9+
- pip

Clone the Repository
~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    $ git clone https://github.com/LuisAlejandro/agoras.git
    $ cd agoras

Install in Dependency Order
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install packages in dependency order to ensure all dependencies are available:

.. code-block:: console

    # Install common (no dependencies)
    $ cd packages/common
    $ pip install -e .

    # Install media (depends on common)
    $ cd ../media
    $ pip install -e .

    # Install core (depends on common + media)
    $ cd ../core
    $ pip install -e .

    # Install platforms (depends on core)
    $ cd ../platforms
    $ pip install -e .

    # Install CLI (depends on platforms)
    $ cd ../cli
    $ pip install -e .

    # Return to project root
    $ cd ../..

**Using editable installs (-e flag):**
  The ``-e`` flag installs packages in "editable" mode, meaning changes to source code are immediately available without reinstalling.

Alternative: Install All at Once
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also install all packages from the project root:

.. code-block:: console

    $ pip install -e packages/common
    $ pip install -e packages/media
    $ pip install -e packages/core
    $ pip install -e packages/platforms
    $ pip install -e packages/cli

Verify Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    $ agoras --version
    $ python3 -c "from agoras.common.version import __version__; print(__version__)"
    $ python3 -c "from agoras.platforms.facebook import Facebook; print('OK')"

Installing Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For running tests and development tools:

.. code-block:: console

    $ pip install -r requirements-dev.txt

This installs pytest, coverage, flake8, and other development tools.

Upgrading
---------

To upgrade to the latest version:

.. code-block:: console

    $ pip install --upgrade agoras

To upgrade a specific package:

.. code-block:: console

    $ pip install --upgrade agoras-platforms

To upgrade from source (development):

.. code-block:: console

    $ git pull
    $ pip install -e packages/cli --upgrade

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Import errors after installation:**
  Ensure all packages are installed in the correct order. If you installed ``agoras-platforms`` but get import errors, try installing dependencies:

  .. code-block:: console

      $ pip install agoras-common agoras-media agoras-core agoras-platforms

**Version conflicts:**
  If you have multiple versions installed, uninstall and reinstall:

  .. code-block:: console

      $ pip uninstall agoras agoras-platforms agoras-core agoras-media agoras-common
      $ pip install agoras

**Development installation not working:**
  Ensure you're using editable installs (``-e`` flag) and installed in dependency order.

**Python version:**
  Agoras requires Python 3.9+. Check your version:

  .. code-block:: console

      $ python3 --version

Getting Help
------------

- **Documentation**: https://agoras.readthedocs.io
- **Issues**: https://github.com/LuisAlejandro/agoras/issues
- **Discord**: https://discord.gg/GRnq3qQ9SB
