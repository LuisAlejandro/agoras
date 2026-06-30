==========================================
Migration Guide: Legacy to New CLI
==========================================

.. note::
   **v2.0 Package Split**: This guide covers CLI migration (v2.0+). For v2.0 package split and import path changes, see the sections below on "Package Installation" and "Import Path Changes".

Overview
========

Agoras uses a platform-first CLI structure that is more intuitive, discoverable, and aligned with how users think about social media operations. This guide helps you migrate from the legacy ``agoras publish`` command to the new ``agoras <platform> <action>`` format.

This migration guide is organized into the following sections:

.. toctree::
   :maxdepth: 1

   installation
   imports
   cli
   platforms
   automation
   testing
   cicd
   reference
   faq
   getting-help

Quick Start
===========

If you're in a hurry, here's the quickest path to migration:

1. **Update Installation**: ``pip install agoras>=2.0.0`` (``>=2.1.0`` if you rely on credential flags on platform actions — that pattern was removed in 2.1.0)
2. **Update Commands**: Replace ``agoras publish --network <platform> --action <action>`` with ``agoras <platform> <action>``
3. **Update Parameters**: Remove platform prefixes (e.g., ``--twitter-consumer-key`` → ``--consumer-key``) and pass credential parameters on ``agoras <platform> authorize`` only (since 2.1.0), not on action commands
4. **Authorize First**: Run ``agoras <platform> authorize`` before actions on all platforms (OAuth via browser for Facebook, Instagram, etc.; CLI credentials or env vars for X, Discord, Telegram, WhatsApp)

For detailed information, see the sections below.
