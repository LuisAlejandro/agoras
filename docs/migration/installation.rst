Package Installation (v2.0+)
==============================

Starting with v2.0, Agoras is split into 5 separate PyPI packages. The main CLI package automatically installs all dependencies.

**Full Installation (Recommended for Most Users):**

.. code-block:: bash

    $ pip install agoras  # Installs all 5 packages including CLI

This installs:
- ``agoras-common``: Utilities, logging, shared constants
- ``agoras-media``: Image and video processing
- ``agoras-core``: Abstract interfaces, Feed, Sheet logic
- ``agoras-platforms``: Platform implementations
- ``agoras``: Command-line interface

**Selective Installation (Advanced Users):**

Install only the packages you need:

.. code-block:: bash

    # Just utilities and logging
    $ pip install agoras-common

    # Media processing (includes common)
    $ pip install agoras-media

    # Core interfaces and business logic (includes common + media)
    $ pip install agoras-core

    # Platform implementations (includes all above)
    $ pip install agoras-platforms

    # CLI tool (includes everything)
    $ pip install agoras

**Package Dependencies:**

The packages follow a layered dependency structure:

.. code-block:: text

   agoras (CLI)
   └── agoras-platforms
       └── agoras-core
           ├── agoras-media
           └── agoras-common

**When to Use Each Package:**

- **Most users**: ``pip install agoras`` (full CLI installation)
- **Python integrations**: ``pip install agoras-platforms`` (no CLI, all platforms)
- **Custom platforms**: ``pip install agoras-core`` (interfaces only)
- **Media processing**: ``pip install agoras-media`` (no social features)
- **Utilities only**: ``pip install agoras-common`` (minimal dependencies)

**Breaking Change:** The monolithic ``agoras`` package structure has been removed. You must install from the new package structure.

Understanding the Package Split
================================

Why Split the Package?
----------------------

The monolithic package structure in v1.x had several limitations:

- **Heavy Dependencies**: All users had to install media processing libraries even if they only needed basic posting
- **Tight Coupling**: Platform implementations were mixed with core interfaces
- **Large Install Size**: Single package contained everything
- **Hard to Extend**: Difficult to build custom integrations without pulling in all dependencies

The v2.0 modular architecture addresses these issues:

- **Selective Installation**: Install only what you need
- **Clear Boundaries**: Each package has a well-defined purpose
- **Smaller Footprint**: Minimal installations for specific use cases
- **Better Extensibility**: Easy to build custom platforms using just ``agoras-core``

Package Responsibilities
------------------------

**agoras-common** (Foundation)
  - Shared utilities and helper functions
  - Logging configuration
  - Version information
  - Depends on: ``requests``, ``beautifulsoup4``

**agoras-media** (Media Processing)
  - Image processing (Pillow)
  - Video processing (OpenCV via ``opencv-python-headless``)
  - Media factory for creating media objects
  - Depends on: ``agoras-common``

**agoras-core** (Business Logic)
  - Abstract ``SocialNetwork`` interface
  - Base API classes
  - Authentication infrastructure
  - Feed automation logic
  - Google Sheets integration
  - Depends on: ``agoras-common``, ``agoras-media``

**agoras-platforms** (Platform Implementations)
  - Concrete platform implementations (Facebook, Twitter, etc.)
  - Platform-specific API clients
  - Platform authentication handlers
  - Depends on: ``agoras-core`` (which includes media and common)

**agoras** (CLI Tool)
  - Command-line interface
  - Platform command handlers
  - Utility commands (feed, schedule)
  - Depends on: ``agoras-platforms`` (which includes all others)

Migration Strategy
------------------

1. **Update Installation**: Change ``pip install agoras`` to ensure you get v2.0+ (or use specific packages)

2. **Update Imports**: Use the import mapping table in :doc:`migration/imports` to update all Python imports

3. **Test Incrementally**: Start with non-critical scripts, then migrate production code

4. **Update CI/CD**: Ensure build pipelines install the correct packages

5. **Check Dependencies**: If you only need specific functionality, consider installing only relevant packages
