==========================================
Migration Guide: Legacy to New CLI
==========================================

.. note::
   **v2.0 Package Split**: This guide covers CLI migration (v2.0+). For v2.0 package split and import path changes, see the sections below on "Package Installation" and "Import Path Changes".

Overview
========

Agoras 2.0+ introduces a new CLI structure that's more intuitive, discoverable, and aligned with how users think about social media operations. This guide helps you migrate from the legacy ``agoras publish`` command to the new platform-first command structure.

This migration guide is organized into the following sections:

.. toctree::
   :maxdepth: 2

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

1. **Update Installation**: ``pip install agoras>=2.0.0``
2. **Update Commands**: Replace ``agoras publish --network <platform> --action <action>`` with ``agoras <platform> <action>``
3. **Update Parameters**: Remove platform prefixes (e.g., ``--twitter-consumer-key`` → ``--consumer-key``)
4. **For OAuth Platforms**: Run ``agoras <platform> authorize`` first

For detailed information, see the sections below.
