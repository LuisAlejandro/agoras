YAML Content Files
==================

.. versionadded:: 2.2

Agoras accepts a single YAML content file via ``--content`` as an alternative to
inline content flags (``--text``, ``--video-url``, ``--image-1``, …). Auth,
routing, and control flags stay on the CLI. The subcommand still owns the
platform and action: ``agoras <platform> <action> --content file.yaml``.

YAML is the only content-file format. Existing commands that print JSON results
are unchanged; content *input* is never JSON.

Rules
-----

* One operation per file (one publish/thread document).
* File must declare ``version: 1``.
* Do not put ``platform``, ``action``, ``kind``, ``network``, or auth fields in YAML.
* Media values must be ``http://`` or ``https://`` URLs (no local paths).
* Unknown or action-incompatible keys are rejected.
* ``--content`` is mutually exclusive with inline content flags.
* Control flags such as ``--recipient``, ``--parse-mode``, ``--loglevel``, and
  Discord channel selection may still appear with ``--content``.

When ``--content`` is used, values from the file win for payload fields.
Environment variables do not override fields that came from the file.

Basic usage
-----------

Inline (unchanged)::

    agoras x post --text "Hello" --link "https://example.com"

YAML file mode::

    agoras x post --content post.yaml

``post.yaml``::

    version: 1
    text: Hello
    link: https://example.com

YouTube video (required fields live in the file)::

    agoras youtube video --content video.yaml

``video.yaml``::

    version: 1
    video_url: https://cdn.example.com/clip.mp4
    title: Demo upload
    description: Optional description
    privacy: private

WhatsApp template (recipient remains a CLI control flag)::

    agoras whatsapp template --content template.yaml --recipient "+15551234567"

``template.yaml``::

    version: 1
    template_name: order_update
    language_code: en_US
    template_components:
      - type: body
        parameters:
          - type: text
            text: "42"

Discord post with embeds::

    agoras discord post --content discord-post.yaml

``discord-post.yaml``::

    version: 1
    text: Release notes
    embeds:
      - title: v2.2
        description: YAML content files
        url: https://example.com/changelog

TikTok photo post (booleans are preserved exactly)::

    agoras tiktok post --content tiktok-post.yaml

``tiktok-post.yaml``::

    version: 1
    images:
      - https://cdn.example.com/1.jpg
      - https://cdn.example.com/2.jpg
    title: Album
    privacy: SELF_ONLY
    allow_comments: false
    brand_organic: false

Unattended TikTok content files must use ``privacy: SELF_ONLY`` (the default). Public privacy and commercial flags fail closed; use interactive ``agoras tiktok post`` / ``video`` so the localhost composer can collect them.

XOR errors
----------

These combinations fail before authentication::

    agoras x post --content post.yaml --text "override"
    agoras youtube video --content video.yaml --video-url https://example.com/a.mp4

Threads (X, Meta Threads, Discord)
----------------------------------

X, Meta Threads, and Discord support a YAML-only ``thread`` action:

* ``agoras x thread --content thread.yaml``
* ``agoras twitter thread --content thread.yaml`` (deprecated alias)
* ``agoras threads thread --content thread.yaml``
* ``agoras discord thread --content thread.yaml``

Constraints:

* ``entries`` must contain 2–100 items.
* Each entry may carry text/link/images **or** one ``video_url``, not both images and video.
* No auto-split of long text; over-limit entries fail before any publish.
* Publishing is ordered and non-transactional: a mid-thread failure leaves earlier
  posts live and does not roll back.
* Output is exactly one JSON envelope (not one ID per entry).

X / Meta Threads example (``thread.yaml``)::

    version: 1
    entries:
      - text: First post
      - text: Follow-up with image
        images:
          - https://cdn.example.com/a.jpg
      - text: Video reply
        video_url: https://cdn.example.com/clip.mp4

Discord requires ``thread_name`` (public text-channel thread)::

    version: 1
    thread_name: Release discussion
    auto_archive_duration: 1440
    entries:
      - text: Starter message
      - text: Second message in the thread
      - embeds:
          - title: Details
            description: More context

Allowed ``auto_archive_duration`` values: ``60``, ``1440``, ``4320``, ``10080``
(minutes).

Thread result envelope
----------------------

Success::

    {"id":"root-id","ids":["root-id","id-2","id-3"],"complete":true}

Discord success may include ``thread_id``.

Confirmed failure after the first entry::

    {"id":"root-id","ids":["root-id"],"complete":false,"failed_index":1,"outcome":"failed","error":"..."}

Ambiguous timeout after dispatch::

    {"id":"root-id","ids":["root-id","id-2"],"complete":false,"failed_index":2,"outcome":"unknown","error":"..."}

Partial or incomplete results exit nonzero. Retry safety is not implied when
``outcome`` is ``unknown``.

Field contracts by action
-------------------------

Root keys depend on ``(platform, action)``. Common post fields:

* ``text``, ``link``, ``images`` (list of up to 4 HTTP(S) URLs)

Common video fields:

* ``video_url`` (required), optional ``text`` / ``video_title`` (platform-specific
  required extras apply — see YouTube, Facebook, Instagram, TikTok)

Thread root fields:

* X / Meta Threads: ``entries``
* Discord: ``thread_name``, optional ``auto_archive_duration``, ``entries``

Platform extras (examples):

* Meta Threads: ``who_can_reply``, ``alt_texts``
* Discord: ``embeds`` (post/video/thread entries)
* TikTok: ``privacy``, ``allow_comments``, ``allow_duet``, ``allow_stitch``,
  ``brand_organic``, ``brand_content``, ``auto_add_music``
* WhatsApp template: ``template_name``, ``language_code``, ``template_components``

For the live matrix of actions, see :doc:`reference/action-support`. For inline
flag names, see :doc:`reference/parameters`.

Reauthorization notes
---------------------

* Meta Threads reply chains require reply-management scope
  (``threads_manage_replies``). Re-run ``agoras threads authorize`` if older
  tokens lack it.
* Discord bots need permission to send messages and create public threads in the
  target text channel.
* X reply chains use the previous tweet ID; account reply settings can still
  deny otherwise valid requests.
