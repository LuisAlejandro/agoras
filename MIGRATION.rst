Migration Guide: Agoras v1.1.3 → v2.0.0
==========================================

This guide helps you migrate from Agoras v1.1.3 (monolithic package) to v2.0.0 (modular package architecture).

Overview
--------

Agoras v2.0 introduces significant changes:

1. **Package Split**: The monolithic package is now split into 5 separate PyPI packages
2. **New Platforms**: Added support for Telegram, WhatsApp, Threads, and X (Twitter rebrand)
3. **OAuth2 Infrastructure**: Automatic OAuth callback server for easier authentication
4. **Async/Await**: All platform operations now use async/await pattern
5. **Unified Architecture**: Consistent three-layer structure across all platforms
6. **Enhanced CLI**: Platform-specific commands with better validation

Breaking Changes
----------------

1. Package Split
~~~~~~~~~~~~~~~~

The monolithic ``agoras`` package is now split into 5 packages:

+-------------+------------------------------------------+--------------------+
| Package     | Purpose                                  | PyPI Name          |
+=============+==========================================+====================+
| Common      | Utilities, logging, version info         | ``agoras-common``  |
+-------------+------------------------------------------+--------------------+
| Media       | Image and video processing               | ``agoras-media``   |
+-------------+------------------------------------------+--------------------+
| Core        | Interfaces, Feed, Sheet, Base API/Auth   | ``agoras-core``    |
+-------------+------------------------------------------+--------------------+
| Platforms   | Platform-specific implementations        | ``agoras-platforms``|
+-------------+------------------------------------------+--------------------+
| CLI         | Command-line interface                   | ``agoras``         |
+-------------+------------------------------------------+--------------------+

When you install ``agoras>=2.0.0``, all 5 packages are automatically installed as dependencies.

2. Import Path Changes
~~~~~~~~~~~~~~~~~~~~~~

All import paths have changed due to the package split.

Most Common Changes (High Impact)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Platform Classes
    # v1.1.3
    from agoras.core.facebook import Facebook

    # v2.0.0
    from agoras.platforms.facebook import Facebook

    # ===

    # Media Processing
    # v1.1.3
    from agoras.core.media import MediaFactory

    # v2.0.0
    from agoras.media import MediaFactory

    # ===

    # Utilities
    # v1.1.3
    from agoras.core.utils import parse_metatags

    # v2.0.0
    from agoras.common.utils import parse_metatags

    # ===

    # Logger
    # v1.1.3
    from agoras.core.logger import logger

    # v2.0.0
    from agoras.common.logger import logger

    # ===

    # Version Info
    # v1.1.3
    from agoras import __version__

    # v2.0.0
    from agoras.common import __version__

All Supported Platforms (v2.0.0)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    from agoras.platforms.facebook import Facebook
    from agoras.platforms.instagram import Instagram
    from agoras.platforms.linkedin import LinkedIn
    from agoras.platforms.discord import Discord
    from agoras.platforms.youtube import YouTube
    from agoras.platforms.tiktok import TikTok
    from agoras.platforms.telegram import Telegram      # New in v2.0
    from agoras.platforms.threads import Threads        # New in v2.0
    from agoras.platforms.whatsapp import WhatsApp      # New in v2.0
    from agoras.platforms.x import X                    # New in v2.0 (Twitter rebrand)

Interface Classes
^^^^^^^^^^^^^^^^^

.. code-block:: python

    # v1.1.3
    from agoras.core.base import SocialNetwork

    # v2.0.0
    from agoras.core.interfaces import SocialNetwork

For a complete import mapping table, see `docs/v2-migration/import-mapping.md <docs/v2-migration/import-mapping.md>`_.

3. Async/Await Pattern
~~~~~~~~~~~~~~~~~~~~~~

All platform methods now use async/await.

.. code-block:: python

    # v1.1.3 (synchronous)
    from agoras.core.facebook import Facebook

    fb = Facebook(facebook_access_token='...')
    fb.post(status_text='Hello', status_link='https://example.com')

    # v2.0.0 (asynchronous)
    import asyncio
    from agoras.platforms.facebook import Facebook

    async def post_to_facebook():
        fb = Facebook(facebook_access_token='...')
        await fb._initialize_client()
        await fb.post(status_text='Hello', status_link='https://example.com')
        await fb.disconnect()

    asyncio.run(post_to_facebook())

4. CLI Command Changes
~~~~~~~~~~~~~~~~~~~~~~

Legacy Command (Still Works with Deprecation Warning)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # v1.1.3 style (deprecated but functional)
    agoras publish --network facebook --action post \
        --status-text "Hello" --status-link "https://example.com"

New Command Structure (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # v2.0.0 style (recommended)
    agoras facebook post \
        --status-text "Hello" --status-link "https://example.com"

Platform-Specific Commands
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Each platform now has its own subcommand:

.. code-block:: bash

    agoras facebook [action]     # Facebook
    agoras instagram [action]    # Instagram
    agoras linkedin [action]     # LinkedIn
    agoras discord [action]      # Discord
    agoras youtube [action]      # YouTube
    agoras tiktok [action]       # TikTok
    agoras telegram [action]     # Telegram (new)
    agoras threads [action]      # Threads (new)
    agoras whatsapp [action]     # WhatsApp (new)
    agoras x [action]            # X/Twitter (new)

Migration Steps
---------------

Step 1: Uninstall v1.1.3
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pip uninstall agoras

Step 2: Install v2.0.0
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    pip install "agoras>=2.0.0"

This automatically installs all 5 sub-packages:

- agoras-common
- agoras-media
- agoras-core
- agoras-platforms
- agoras (CLI)

Step 3: Update Your Code
~~~~~~~~~~~~~~~~~~~~~~~~~

Option A: Automated (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use find-and-replace to update imports:

.. code-block:: bash

    # Find all Python files with old imports
    find . -name "*.py" -type f -exec sed -i '' \
        's/from agoras\.core\.facebook import/from agoras.platforms.facebook import/g' {} +

    find . -name "*.py" -type f -exec sed -i '' \
        's/from agoras\.core\.media import/from agoras.media import/g' {} +

    find . -name "*.py" -type f -exec sed -i '' \
        's/from agoras\.core\.utils import/from agoras.common.utils import/g' {} +

    # ... (repeat for other common imports)

Option B: Manual
^^^^^^^^^^^^^^^^

1. Scan your code for ``from agoras`` imports
2. Update each import using the `import mapping table <docs/v2-migration/import-mapping.md>`_
3. Test your code after each update

Step 4: Convert to Async/Await
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update your platform usage to use async/await:

.. code-block:: python

    # Before (v1.1.3)
    def post_content():
        fb = Facebook(facebook_access_token='...')
        fb.post(status_text='Hello', status_link='https://example.com')

    # After (v2.0.0)
    import asyncio

    async def post_content():
        fb = Facebook(facebook_access_token='...')
        await fb._initialize_client()
        try:
            await fb.post(status_text='Hello', status_link='https://example.com')
        finally:
            await fb.disconnect()

    # Run it
    asyncio.run(post_content())

Step 5: Update CLI Scripts
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have shell scripts using the CLI:

.. code-block:: bash

    # Before (v1.1.3)
    #!/bin/bash
    agoras publish --network facebook --action post \
        --facebook-access-token "$TOKEN" \
        --status-text "Hello" \
        --status-link "https://example.com"

    # After (v2.0.0)
    #!/bin/bash
    agoras facebook post \
        --facebook-access-token "$TOKEN" \
        --status-text "Hello" \
        --status-link "https://example.com"

Step 6: Test Your Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Run your test suite
2. Verify authentication still works
3. Test posting to each platform you use
4. Check error handling and logging

CI/CD Migration
---------------

If you use Agoras in your CI/CD pipeline, update your workflows:

GitHub Actions
~~~~~~~~~~~~~~

**Before (v1.1.3):**

.. code-block:: yaml

    - name: Install Agoras
      run: pip install agoras==1.1.3

    - name: Post to social media
      run: |
        agoras publish --network facebook --action post \
          --facebook-access-token "${{ secrets.FB_TOKEN }}" \
          --status-text "Deployed!"

**After (v2.0.0):**

.. code-block:: yaml

    - name: Install Agoras
      run: pip install "agoras>=2.0.0"

    - name: Post to social media
      run: |
        agoras facebook post \
          --facebook-access-token "${{ secrets.FB_TOKEN }}" \
          --status-text "Deployed!"

Dependency Pinning
~~~~~~~~~~~~~~~~~~

For reproducible builds:

.. code-block:: bash

    # Pin exact version
    agoras==2.0.0

    # Pin major version (recommended)
    agoras>=2.0.0,<3.0.0

    # Install specific sub-packages (advanced)
    agoras-common==2.0.0
    agoras-media==2.0.0
    agoras-core==2.0.0
    agoras-platforms==2.0.0
    agoras==2.0.0

Docker/Container Environments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update your Dockerfile:

.. code-block:: dockerfile

    # Before
    RUN pip install agoras==1.1.3

    # After
    RUN pip install "agoras>=2.0.0"

Test Migration
--------------

Update Your Test Imports
~~~~~~~~~~~~~~~~~~~~~~~~~

**Before (v1.1.3):**

.. code-block:: python

    # tests/test_facebook.py
    from agoras.core.facebook import Facebook
    from agoras.core.media import MediaFactory
    from agoras.core.utils import parse_metatags

    def test_facebook_post():
        fb = Facebook(facebook_access_token='test_token')
        fb.post(status_text='Test')

**After (v2.0.0):**

.. code-block:: python

    # tests/test_facebook.py
    import pytest
    from agoras.platforms.facebook import Facebook
    from agoras.media import MediaFactory
    from agoras.common.utils import parse_metatags

    @pytest.mark.asyncio
    async def test_facebook_post():
        fb = Facebook(facebook_access_token='test_token')
        await fb._initialize_client()
        try:
            await fb.post(status_text='Test')
        finally:
            await fb.disconnect()

Mock Strategy Changes
~~~~~~~~~~~~~~~~~~~~~

Update mocks for async methods:

.. code-block:: python

    # Before (v1.1.3)
    from unittest.mock import Mock, patch

    @patch('agoras.core.facebook.Facebook.post')
    def test_post(mock_post):
        mock_post.return_value = {'id': '123'}
        fb = Facebook(facebook_access_token='test')
        result = fb.post(status_text='Test')
        assert result['id'] == '123'

    # After (v2.0.0)
    from unittest.mock import AsyncMock, patch
    import pytest

    @pytest.mark.asyncio
    @patch('agoras.platforms.facebook.Facebook.post', new_callable=AsyncMock)
    async def test_post(mock_post):
        mock_post.return_value = {'id': '123'}
        fb = Facebook(facebook_access_token='test')
        await fb._initialize_client()
        try:
            result = await fb.post(status_text='Test')
            assert result['id'] == '123'
        finally:
            await fb.disconnect()

Pytest Configuration
~~~~~~~~~~~~~~~~~~~~

Add pytest-asyncio to your test dependencies:

.. code-block:: bash

    # requirements-dev.txt or test dependencies
    pytest>=7.0.0
    pytest-asyncio>=0.21.0
    pytest-cov>=4.0.0

Update pytest.ini:

.. code-block:: ini

    [pytest]
    asyncio_mode = auto
    testpaths = tests
    python_files = test_*.py
    python_classes = Test*
    python_functions = test_*

Platform-Specific Notes
-----------------------

Facebook
~~~~~~~~

- OAuth2 callback server now available (no manual URL copy-paste)
- Support for Reels and Stories
- Enhanced video upload

Instagram
~~~~~~~~~

- OAuth2 improvements
- Better media validation

LinkedIn
~~~~~~~~

- OAuth2 callback server
- Enhanced post formatting

TikTok
~~~~~~

- Improved video handling
- OAuth2 support

YouTube
~~~~~~~

- Better video upload flow
- OAuth2 enhancements

New Platforms (v2.0)
~~~~~~~~~~~~~~~~~~~~

Telegram
^^^^^^^^

.. code-block:: python

    from agoras.platforms.telegram import Telegram

    async def post_to_telegram():
        tg = Telegram(telegram_bot_token='...', telegram_chat_id='...')
        await tg._initialize_client()
        await tg.post(status_text='Hello Telegram!', status_link='https://example.com')
        await tg.disconnect()

Threads
^^^^^^^

.. code-block:: python

    from agoras.platforms.threads import Threads

    async def post_to_threads():
        th = Threads(threads_access_token='...')
        await th._initialize_client()
        await th.post(status_text='Hello Threads!', status_link='https://example.com')
        await th.disconnect()

WhatsApp
^^^^^^^^

.. code-block:: python

    from agoras.platforms.whatsapp import WhatsApp

    async def send_to_whatsapp():
        wa = WhatsApp(whatsapp_access_token='...', whatsapp_phone_number_id='...')
        await wa._initialize_client()
        await wa.post(status_text='Hello WhatsApp!', status_link='https://example.com')
        await wa.disconnect()

X (Twitter)
^^^^^^^^^^^

.. code-block:: python

    from agoras.platforms.x import X

    async def post_to_x():
        x_platform = X(x_api_key='...', x_api_secret='...', x_access_token='...', x_access_token_secret='...')
        await x_platform._initialize_client()
        await x_platform.post(status_text='Hello X!', status_link='https://example.com')
        await x_platform.disconnect()

FAQ
---

Q: Can I still use v1.1.3?
~~~~~~~~~~~~~~~~~~~~~~~~~~

**A:** Yes, v1.1.3 will remain available on PyPI indefinitely. You can pin to ``agoras==1.1.3`` if you're not ready to migrate.

Q: Will v1.1.3 receive updates?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**A:** Only critical security patches. New features and bug fixes will only be added to v2.0+.

Q: Do I need to install all 5 packages separately?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**A:** No. Installing ``agoras>=2.0.0`` automatically installs all dependencies.

Q: Can I install only specific sub-packages?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**A:** Yes, for advanced use cases:

.. code-block:: bash

    pip install agoras-media  # Only media processing
    pip install agoras-core   # Core + media + common

However, most users should install the main ``agoras`` package.

Q: What if my imports still don't work?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**A:** Check the `import mapping table <docs/v2-migration/import-mapping.md>`_ for the correct import path. If you're still stuck, open an issue on GitHub.

Q: How do I migrate OAuth credentials?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**A:** OAuth credentials remain the same. The v2.0 OAuth callback server makes authentication easier, but existing tokens continue to work.

Q: Are there CLI compatibility shims?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**A:** Yes, legacy ``publish`` commands still work but emit deprecation warnings. They will be removed in v3.0.

Q: Will this affect my scheduled posts?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**A:** No, configuration files and environment variables use the same format. Only code imports need updating.

Getting Help
------------

- **Documentation**: https://agoras.readthedocs.io
- **GitHub Issues**: https://github.com/LuisAlejandro/agoras/issues
- **Migration Issues**: Tag with ``migration`` label

See Also
--------

- `Import Mapping Table <docs/v2-migration/import-mapping.md>`_ - Complete import path reference
- `v2.0 Features <docs/v2-migration/v2-features.md>`_ - All new features in v2.0
- `Dependency Graph <docs/v2-migration/dependency-graph.md>`_ - Architecture analysis
- `CHANGELOG <HISTORY.rst>`_ - Detailed change history
