CI/CD Migration
===============

If you use Agoras in your CI/CD pipeline, update your workflows to use the new package structure and commands.

GitHub Actions
--------------

**Before (v1.x):**

.. code-block:: yaml

    - name: Install Agoras
      run: pip install agoras==1.1.3

    - name: Post to social media
      run: |
        agoras publish --network facebook --action post \
          --facebook-access-token "${{ secrets.FB_TOKEN }}" \
          --status-text "Deployed!"

**After (v2.0):**

.. code-block:: yaml

    - name: Install Agoras
      run: pip install "agoras>=2.0.0"

    - name: Post to social media
      run: |
        agoras facebook post \
          --text "Deployed!"

**Note:** For OAuth platforms, ensure you've authorized before running CI/CD. Tokens are stored locally, so you may need to set up token storage in your CI environment or use environment variables for API key-based platforms.

Dependency Pinning
------------------

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
------------------------------

Update your Dockerfile:

.. code-block:: dockerfile

    # Before
    RUN pip install agoras==1.1.3

    # After
    RUN pip install "agoras>=2.0.0"
