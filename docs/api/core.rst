agoras.core package
===================

The ``agoras.core`` package provides abstract interfaces, business logic, and shared infrastructure for all Agoras platform implementations.

Package Overview
----------------

This package provides:
- Abstract ``SocialNetwork`` interface that all platforms must implement
- Base API classes for platform API clients
- Authentication infrastructure (OAuth2, token storage, callback server)
- Feed management for RSS/Atom feed automation
- Sheet management for Google Sheets scheduling

**Dependencies:** Requires ``agoras-common`` and ``agoras-media``.

agoras.core package
-------------------

.. automodule:: agoras.core
    :members:
    :undoc-members:
    :show-inheritance:

agoras.core.interfaces module
-----------------------------

Abstract interface that all social network platforms must implement.

.. automodule:: agoras.core.interfaces
    :members:
    :undoc-members:
    :show-inheritance:

agoras.core.api_base module
----------------------------

Base API class for platform API client implementations.

.. automodule:: agoras.core.api_base
    :members:
    :undoc-members:
    :show-inheritance:

agoras.core.auth package
------------------------

OAuth2 authentication infrastructure for Agoras.

This package provides base classes and utilities for OAuth2 authentication across all social media platforms.

agoras.core.auth package
-------------------------

.. automodule:: agoras.core.auth
    :members:
    :undoc-members:
    :show-inheritance:

agoras.core.auth.base module
-----------------------------

Base authentication manager for OAuth2 flows.

.. automodule:: agoras.core.auth.base
    :members:
    :undoc-members:
    :show-inheritance:

agoras.core.auth.storage module
--------------------------------

Secure token storage for OAuth2 credentials.

.. automodule:: agoras.core.auth.storage
    :members:
    :undoc-members:
    :show-inheritance:

agoras.core.auth.callback_server module
----------------------------------------

OAuth2 callback server for handling authorization redirects.

.. automodule:: agoras.core.auth.callback_server
    :members:
    :undoc-members:
    :show-inheritance:

agoras.core.auth.exceptions module
-----------------------------------

Authentication-related exceptions.

.. automodule:: agoras.core.auth.exceptions
    :members:
    :undoc-members:
    :show-inheritance:
