Testing Your Migration
=======================

Preview Mode
------------

Use the ``--show-migration`` flag to preview the new command without executing::

    agoras publish --network twitter --action post \
      --twitter-consumer-key "$KEY" \
      --status-text "Test" \
      --show-migration

This will show::

    Migration Preview:
      Old: agoras publish --network twitter --action post [options]
      New: agoras x post --consumer-key "$KEY" --text "Test"

    No action executed (preview mode)

Platform-Specific Help
----------------------

Explore new commands using help::

    # See all platforms
    agoras --help

    # See X actions
    agoras x --help

    # See X post options
    agoras x post --help

    # See utils commands
    agoras utils --help

    # See feed-publish options
    agoras utils feed-publish --help

Gradual Migration Strategy
===========================

1. **Week 1**: Test migration using ``--show-migration`` flag
2. **Week 2**: Migrate non-critical scripts to new format
3. **Week 3**: Update CI/CD pipelines with new commands
4. **Week 4**: Migrate production scripts
5. **Ongoing**: Keep legacy as fallback until comfortable

Remember: The legacy ``agoras publish`` command remains available with deprecation warnings through Agoras 2.x and will be removed in Agoras 3.0.

Test Migration
===============

If you have automated tests for your Agoras integration, you'll need to update them for v2.0.

Update Your Test Imports
------------------------

**Before (v1.x):**

.. code-block:: python

    # tests/test_facebook.py
    from agoras.core.facebook import Facebook
    from agoras.core.media import MediaFactory
    from agoras.core.utils import parse_metatags

    def test_facebook_post():
        fb = Facebook(facebook_access_token='test_token')
        fb.post(status_text='Test')

**After (v2.0):**

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
---------------------

Update mocks for async methods:

**Before (v1.x):**

.. code-block:: python

    from unittest.mock import Mock, patch

    @patch('agoras.core.facebook.Facebook.post')
    def test_post(mock_post):
        mock_post.return_value = {'id': '123'}
        fb = Facebook(facebook_access_token='test')
        result = fb.post(status_text='Test')
        assert result['id'] == '123'

**After (v2.0):**

.. code-block:: python

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

**Key Changes:**

- Use ``AsyncMock`` instead of ``Mock`` for async methods
- Use ``@pytest.mark.asyncio`` decorator on test functions
- Use ``new_callable=AsyncMock`` in ``@patch`` decorators
- Make test functions ``async`` and use ``await``

Pytest Configuration
--------------------

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

The ``asyncio_mode = auto`` setting automatically detects async test functions and runs them with asyncio.
