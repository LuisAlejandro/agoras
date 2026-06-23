Automation Commands Migration
==============================

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

New::

    agoras utils feed-publish \
      --network x \
      --mode last \
      --feed-url "https://example.com/feed.xml" \
      --max-count 1 \
      --x-consumer-key "$KEY" \
      --x-consumer-secret "$SECRET" \
      --x-oauth-token "$TOKEN" \
      --x-oauth-secret "$OAUTH_SECRET"

.. note::
   The ``--network twitter`` and ``--twitter-*`` parameters are deprecated. Use ``--network x`` and ``--x-*`` parameters instead.

**Publishing Random Entry from Feed**

Legacy::

    agoras publish --network facebook --action random-from-feed \
      --feed-url "https://example.com/feed.xml" \
      --facebook-access-token "$TOKEN"

New (v2.0+)::

    # After authorization
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

New::

    agoras utils schedule-run \
      --network x \
      --sheets-id "$SHEET_ID" \
      --sheets-name "Schedule" \
      --sheets-client-email "$EMAIL" \
      --sheets-private-key "$KEY" \
      --x-consumer-key "$KEY"

.. note::
   The ``--network twitter`` and ``--twitter-*`` parameters are deprecated. Use ``--network x`` and ``--x-*`` parameters instead.
