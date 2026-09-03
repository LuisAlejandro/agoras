agoras.cli package
==================

The ``agoras.cli`` package provides the command-line interface for Agoras, enabling interaction with social media platforms through a unified CLI.

Package Overview
----------------

This package provides:

- Main entry point (`agoras.cli.main`) for the ``agoras`` command-line tool
- Platform-specific command parsers for all 10 supported platforms
- Utility commands for feed automation and scheduling
- Platform registry for managing platform actions

**Dependencies:** Requires ``agoras-platforms>=2.0.0``.

Entry Point
-----------

The CLI is installed as a console script entry point:

.. code-block:: bash

   agoras [options] <command> [options]

See :doc:`usage` for detailed usage examples.

agoras.cli package
-------------------

.. automodule:: agoras.cli
    :members:
    :undoc-members:
    :show-inheritance:

agoras.cli.main module
----------------------

Main entry point for the CLI application.

.. automodule:: agoras.cli.main
    :members:
    :undoc-members:
    :show-inheritance:

agoras.cli.base module
-----------------------

Base utilities for CLI argument parsing and common options.

.. automodule:: agoras.cli.base
    :members:
    :undoc-members:
    :show-inheritance:

agoras.cli.registry module
--------------------------

Platform registry for managing supported platforms and their actions.

.. automodule:: agoras.cli.registry
    :members:
    :undoc-members:
    :show-inheritance:

agoras.cli.commands package
---------------------------

CLI command implementations.

agoras.cli.commands package
---------------------------

.. automodule:: agoras.cli.commands
    :members:
    :undoc-members:
    :show-inheritance:

agoras.cli.utils package
-------------------------

Utility commands for automation (feed, scheduling).

agoras.cli.utils package
-------------------------

.. automodule:: agoras.cli.utils
    :members:
    :undoc-members:
    :show-inheritance:

agoras.cli.utils.feed module
------------------------------

Feed automation utilities for RSS/Atom feeds.

.. automodule:: agoras.cli.utils.feed
    :members:
    :undoc-members:
    :show-inheritance:

agoras.cli.utils.schedule module
----------------------------------

Scheduling utilities for Google Sheets integration.

.. automodule:: agoras.cli.utils.schedule
    :members:
    :undoc-members:
    :show-inheritance:

agoras.cli.validator module
---------------------------

Validation utilities for CLI parameters.

.. automodule:: agoras.cli.validator
    :members:
    :undoc-members:
    :show-inheritance:

agoras.cli.converter module
---------------------------

Conversion utilities for CLI data formats.

.. automodule:: agoras.cli.converter
    :members:
    :undoc-members:
    :show-inheritance:

agoras.cli.publish_stub module
-----------------------------

Pointer stub for the legacy ``agoras publish`` command, removed in Agoras 3.0.

.. automodule:: agoras.cli.publish_stub
