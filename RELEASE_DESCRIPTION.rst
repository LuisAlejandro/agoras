Agoras is a modular Python command-line utility for publishing, managing, and automating
posts across 10 major social networks including X, Facebook, Instagram, LinkedIn, Discord,
YouTube, TikTok, Threads, Telegram, and WhatsApp. Version 3.0 completes the platform-first
CLI: the legacy ``agoras publish`` command is gone, and credentials are stored under
``app@account`` profiles, so several apps can drive the same account without overwriting
each other. Credentials supplied through environment variables keep working unchanged as a
self-contained profile.

Stored credentials are not read across this upgrade. Re-authorize every account once with
``agoras <platform> authorize`` before the next post, then select a profile with
``--profile`` when an account has more than one.
