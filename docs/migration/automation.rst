Automation Commands Migration
==============================

Utils automation (``feed-publish``, ``schedule-run``) invokes platform wrappers
through the shared platform runner, not ``agoras publish``.

Feed Automation
---------------

**Publishing Last Entry from Feed**

Legacy::

    agoras publish --network twitter --action last-from-feed \
      --feed-url "https://example.com/feed.xml" \
      --feed-max-count 1 \
      --twitter-consumer-key "$KEY" \
      --twitter-consumer-secret "$SECRET" \
      --twitter-oauth-token "$TOKEN" \
      --twitter-oauth-secret "$OAUTH_SECRET"

New (2.1.0+)::

    # Authorize once, or set TWITTER_* env vars for CI
    agoras utils feed-publish \
      --network x \
      --mode last \
      --feed-url "https://example.com/feed.xml" \
      --max-count 1

.. note::
   The ``--network twitter`` alias is deprecated. Use ``--network x`` instead.
   Utils commands accept ``twitter`` silently (no stderr warning); legacy
   ``agoras publish`` still emits a deprecation warning.

**Publishing Random Entry from Feed**

Legacy::

    agoras publish --network facebook --action random-from-feed \
      --feed-url "https://example.com/feed.xml" \
      --facebook-access-token "$TOKEN"

New (2.1.0+)::

    agoras utils feed-publish \
      --network facebook \
      --mode random \
      --feed-url "https://example.com/feed.xml"

Schedule Automation
-------------------

**Running Scheduled Posts**

Legacy::

    agoras publish --network twitter --action schedule \
      --google-sheets-id "$SHEET_ID" \
      --google-sheets-name "Schedule" \
      --google-sheets-client-email "$EMAIL" \
      --google-sheets-private-key "$KEY" \
      --twitter-consumer-key "$KEY"

New (2.1.0+)::

    agoras utils schedule-run \
      --network x \
      --sheets-id "$SHEET_ID" \
      --sheets-name "Schedule" \
      --sheets-client-email "$EMAIL" \
      --sheets-private-key "$KEY"

.. note::
   ``schedule-run`` requires ``--network``. Run separate jobs for each platform. The ``--network twitter`` alias is deprecated; use ``--network x``.
