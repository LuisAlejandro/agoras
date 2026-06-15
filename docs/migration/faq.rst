Frequently Asked Questions
===========================

Installation & Packages
-----------------------

Q: Do I need to install all 5 packages separately?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: No. Installing ``pip install agoras`` automatically installs all 5 packages as dependencies. You only need to install packages separately if you want to use Agoras as a Python library without the CLI.

Q: Can I install only specific packages?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Yes, for advanced use cases. See :doc:`migration/installation` for details. Most users should install the main ``agoras`` package.

Q: What's the difference between ``agoras`` and ``agoras-platforms``?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: The ``agoras`` package includes the CLI tool and all dependencies. The ``agoras-platforms`` package includes all platform implementations but no CLI - use it if you're building Python integrations without the command-line interface.

CLI Commands
------------

Q: Why did the command format change?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: The new format is more intuitive and discoverable. Instead of ``agoras publish --network twitter --action post``, you now use ``agoras x post``. This makes it easier to discover what actions each platform supports and reduces command length.

Q: Can I still use ``agoras publish``?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Yes, the legacy ``agoras publish`` command still works but shows deprecation warnings. It is supported through all Agoras 2.x releases and will be removed in Agoras 3.0. We recommend migrating to the new format as soon as possible.

Q: What's the difference between platform commands and utils commands?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: **Platform commands** (e.g., ``agoras x post``) are for direct platform operations and use simplified parameter names (``--consumer-key`` instead of ``--x-consumer-key``). **Utils commands** (e.g., ``agoras utils feed-publish``) are for automation tasks and use prefixed parameters to support multiple platforms in one command.

Q: Why do utils commands use prefixed parameters?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Utils commands need to support multiple platforms, so they use prefixed parameters (e.g., ``--x-consumer-key``, ``--facebook-object-id``) to avoid conflicts when specifying credentials for different platforms in the same command.

OAuth 2.0 Authentication
------------------------

Q: Why do I need to run ``authorize`` first for some platforms?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: OAuth 2.0 platforms (Facebook, Instagram, LinkedIn, YouTube, TikTok, Threads) require a one-time authorization step. This is more secure than passing tokens directly and allows automatic token refresh. Bot-based platforms (Discord, Telegram) and API key platforms (X) don't require this step.

Q: Do I need to re-authorize if I upgrade?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: No. Once you've authorized, your tokens are stored securely and persist across upgrades. You only need to re-authorize if you revoke access or if your tokens expire.

Q: Where are tokens stored?
~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Tokens are stored in a secure location on your system. The exact location depends on your operating system. See :doc:`../api/core_api` for details on token storage. For more information, check the authentication documentation in the API reference.

Q: How do I revoke authorization?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: You can revoke authorization through the platform's developer console (Facebook Developer Portal, Google Cloud Console, etc.). Agoras will automatically detect revoked tokens and prompt you to re-authorize.

Parameter Names
---------------

Q: Why did parameter names change?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Parameter names were simplified for better usability. For example, ``--status-text`` became ``--text``, and ``--twitter-consumer-key`` became ``--consumer-key`` in platform commands. This makes commands shorter and easier to remember.

Q: Can I still use old parameter names?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: In platform commands, old parameter names are not supported. In utils commands, some deprecated parameter names (like ``--twitter-*``) still work but show deprecation warnings. See :doc:`migration/reference` for the complete parameter reference.

Q: Why are some parameters different in utils commands?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Utils commands support multiple platforms, so they use prefixed parameters (e.g., ``--x-consumer-key``) to avoid conflicts. Platform commands only work with one platform, so they use simplified names (e.g., ``--consumer-key``).

Import Paths (Python)
---------------------

Q: Do I need to update my Python imports?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Yes, if you're using Agoras as a Python library. All import paths have changed due to the package split. See the :doc:`migration/imports` section for a complete mapping.

Q: Where can I find the import mapping?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: See the :doc:`migration/imports` section. It provides comprehensive tables mapping old v1.x imports to new v2.0 imports.

Q: What if my imports don't work?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: First, ensure you've installed the correct packages. If you're using ``agoras-platforms``, make sure it's installed. If you're using ``agoras-core``, ensure all dependencies are installed. Check the import mapping table and verify your import paths match the new structure. If issues persist, open an issue on GitHub.

Migration Timeline
------------------

Q: How long will legacy commands be supported?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: The legacy ``agoras publish`` command is supported with deprecation warnings through all Agoras 2.x releases and will be removed in Agoras 3.0. We recommend migrating as soon as possible.

Q: When should I migrate?
~~~~~~~~~~~~~~~~~~~~~~~~

A: You can migrate at any time. The legacy commands still work, so you can migrate gradually. We recommend starting with non-critical scripts, then moving to production code once you're comfortable with the new format.

Q: Can I migrate gradually?
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Yes! You can use both old and new commands during the transition period. Start by migrating new scripts to the new format, then gradually update existing scripts. The ``--show-migration`` flag can help you preview the new command format.

Common Migration Pitfalls
==========================

1. **Forgetting to remove platform prefix**

   Wrong::

       agoras x post --twitter-consumer-key "$KEY"

   Correct::

       agoras x post --consumer-key "$KEY"

2. **Using old parameter names**

   Wrong::

       agoras x post --status-text "Hello"

   Correct::

       agoras x post --text "Hello"

3. **Using deprecated twitter command**

   Wrong::

       agoras twitter post --consumer-key "$KEY"

   Correct::

       agoras x post --consumer-key "$KEY"

4. **Using platform command for feed automation**

   Wrong::

       agoras x last-from-feed --feed-url "feed.xml"

   Correct::

       agoras utils feed-publish --network x --mode last --feed-url "feed.xml"

5. **Forgetting --network in utils commands**

   Wrong::

       agoras utils feed-publish --mode last --feed-url "feed.xml"

   Correct::

       agoras utils feed-publish --network x --mode last --feed-url "feed.xml"

6. **Using deprecated parameters in utils commands**

   Wrong::

       agoras utils feed-publish --network twitter --twitter-consumer-key "$KEY"

   Correct::

       agoras utils feed-publish --network x --x-consumer-key "$KEY"

Troubleshooting
===============

Q: I get "command not found" errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Ensure Agoras is installed correctly: ``pip install agoras``. Verify the installation: ``agoras --version``. If using a virtual environment, make sure it's activated. Check that the ``agoras`` command is in your PATH.

Q: My old scripts don't work
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Old scripts using ``agoras publish`` should still work but may show deprecation warnings. If they fail completely, check:
- Are you using the correct parameter names?
- Have you updated to v2.0+?
- Are all required parameters provided?
- For OAuth platforms, have you run ``authorize`` first?

Q: I see deprecation warnings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Deprecation warnings indicate you're using old commands or parameters that will be removed in Agoras 3.0 (legacy ``agoras publish`` is supported through all 2.x releases). Update your commands to the new format. The warnings won't break your scripts, but you should migrate before upgrading to 3.0.

Q: OAuth authorization fails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Check that:
- Your app credentials (client ID, client secret) are correct
- Your redirect URI matches what's configured in the platform's developer console
- You have the necessary permissions/scopes enabled in your app
- Your app is approved for production use (if required by the platform)

Q: Platform command says "not authorized"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: For OAuth platforms, you must run ``agoras <platform> authorize`` first. After authorization, tokens are stored and you don't need to authorize again unless you revoke access.

Q: Utils command fails with "network not specified"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A: Utils commands require the ``--network`` parameter to specify which platform to use. For example: ``agoras utils feed-publish --network x --mode last ...``
