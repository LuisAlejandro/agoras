Agoras Packages
===============

This directory contains the modular package structure for Agoras v2.0.

Package Structure
-----------------

Agoras is split into 5 independent packages:

1. agoras-common
~~~~~~~~~~~~~~~~

**Location**: ``packages/common/``

**Purpose**: Low-level utilities, logging, and shared constants

**Dependencies**: None

2. agoras-media
~~~~~~~~~~~~~~~

**Location**: ``packages/media/``

**Purpose**: Image and video processing

**Dependencies**: agoras-common

3. agoras-core
~~~~~~~~~~~~~~

**Location**: ``packages/core/``

**Purpose**: Interfaces (SocialNetwork), Feed, Sheet, Base API/Auth classes

**Dependencies**: agoras-common, agoras-media

4. agoras-platforms
~~~~~~~~~~~~~~~~~~~

**Location**: ``packages/platforms/``

**Purpose**: Platform-specific implementations (Facebook, Twitter, etc.)

**Dependencies**: agoras-core

5. agoras (CLI)
~~~~~~~~~~~~~~~

**Location**: ``packages/cli/``

**Purpose**: Command-line interface and main entry point

**Dependencies**: agoras-platforms

Development Setup
-----------------

To work on all packages simultaneously:

.. code-block:: bash

   # Install all packages in editable mode
   pip install -e packages/common
   pip install -e packages/media
   pip install -e packages/core
   pip install -e packages/platforms
   pip install -e packages/cli

Testing
-------

Each package has its own test suite:

.. code-block:: bash

   # Test individual package
   cd packages/common
   pytest tests/

   # Test all packages
   tox

Building
--------

Each package can be built independently:

.. code-block:: bash

   cd packages/common
   python setup.py sdist bdist_wheel

Publishing
----------

All packages are published to PyPI:

.. code-block:: bash

   # Publish all packages (in dependency order)
   twine upload packages/common/dist/*
   twine upload packages/media/dist/*
   twine upload packages/core/dist/*
   twine upload packages/platforms/dist/*
   twine upload packages/cli/dist/*

Status
------

Week 2 Complete ✅
~~~~~~~~~~~~~~~~~~

- ✅ **agoras-common** - Extracted, tested, and built (v2.0.0)
- ✅ **agoras-media** - Extracted, tested, and built (v2.0.0)
- ✅ **agoras-core** - Extracted, tested, and built (v2.0.0)
- ✅ **agoras-platforms** - Extracted, tested, and built (v2.0.0)
- 🚧 **agoras (CLI)** - Week 3 (pending)

**Progress**: 4/5 packages complete (80%)

Files will continue to be migrated according to the `Package Split Plan <../.cursor/plans/package-split/PACKAGE_SPLIT_PLAN.md>`_.
