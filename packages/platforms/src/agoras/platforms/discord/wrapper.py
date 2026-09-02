# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
# Copyright (C) 2022-2026, Agoras Developers.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""agoras.platforms.discord.wrapper module."""

import asyncio
from typing import Any, Dict, List, Optional

import discord

from agoras.common.utils import parse_metatags
from agoras.core.interfaces import SocialNetwork, _entry_images, _is_uncertain_publish_error
from agoras.core.text_limits import validate_discord_embeds, validate_text
from agoras.core.threading import (
    ThreadPublishError,
    ThreadResult,
    partial_result,
    success_result,
)
from agoras.media.paths import media_is_local

from .api import DiscordAPI

_DISCORD_ARCHIVE_DURATIONS = frozenset({60, 1440, 4320, 10080})


class Discord(SocialNetwork):
    """
    Discord social network implementation.

    This class provides Discord-specific functionality for posting messages,
    videos, and managing Discord interactions asynchronously.
    """

    # Pure-proxy platform: delete_reply/get_reply delegate to delete/get_post
    _proxy_delete_reply = True
    _proxy_get_reply = True

    def __init__(self, **kwargs):
        """
        Initialize Discord instance.

        Args:
            **kwargs: Configuration parameters including:
                - discord_bot_token: Discord bot token
                - discord_server_name: Discord server name
                - discord_channel_name: Discord channel name
        """
        # Map platform-specific keys to generic keys for core interface compatibility
        if "discord_post_id" in kwargs:
            kwargs["post_id"] = kwargs["discord_post_id"]
        if "discord_video_url" in kwargs:
            kwargs["video_url"] = kwargs["discord_video_url"]
        if "discord_video_title" in kwargs:
            kwargs["video_title"] = kwargs["discord_video_title"]

        super().__init__(**kwargs)
        self.discord_bot_token = None
        self.discord_server_name = None
        self.discord_channel_name = None

    async def _initialize_client(self):
        """
        Initialize Discord API client.

        This method sets up the Discord API client with configuration.
        Tries to load credentials from storage if not provided via parameters.
        """
        self.discord_bot_token = self._get_auth_config_value("discord_bot_token", "DISCORD_BOT_TOKEN")
        self.discord_server_name = self._get_auth_config_value("discord_server_name", "DISCORD_SERVER_NAME")
        self.discord_channel_name = self._get_auth_config_value("discord_channel_name", "DISCORD_CHANNEL_NAME")

        # If credentials not provided, try loading from storage
        if not all([self.discord_bot_token, self.discord_server_name, self.discord_channel_name]):
            from .auth import DiscordAuthManager

            auth_manager = DiscordAuthManager(
                bot_token=self.discord_bot_token,
                server_name=self.discord_server_name,
                channel_name=self.discord_channel_name,
                profile=self._get_config_value("profile"),
            )

            if auth_manager._load_credentials_from_storage():
                # Fill in missing credentials from storage
                if not self.discord_bot_token:
                    self.discord_bot_token = auth_manager.bot_token
                if not self.discord_server_name:
                    self.discord_server_name = auth_manager.server_name
                if not self.discord_channel_name:
                    self.discord_channel_name = auth_manager.channel_name

        # Validate all credentials are now available
        if not all([self.discord_bot_token, self.discord_server_name, self.discord_channel_name]):
            raise Exception("Not authenticated. Please run 'agoras discord authorize' first.")

        # Initialize Discord API
        self.api = DiscordAPI(self.discord_bot_token, self.discord_server_name, self.discord_channel_name)

        # Authenticate with provided credentials
        await self.api.authenticate()

    async def authorize_credentials(self):
        """
        Authorize and store Discord credentials for future use.

        Returns:
            bool: True if authorization successful
        """
        from .auth import DiscordAuthManager

        bot_token = self._get_config_value("discord_bot_token", "DISCORD_BOT_TOKEN")
        server_name = self._get_config_value("discord_server_name", "DISCORD_SERVER_NAME")
        channel_name = self._get_config_value("discord_channel_name", "DISCORD_CHANNEL_NAME")

        auth_manager = DiscordAuthManager(
            bot_token=bot_token,
            server_name=server_name,
            channel_name=channel_name,
            profile=self._get_config_value("profile"),
        )

        result = await auth_manager.authorize()
        if result:
            print(result)
            return True
        return False

    async def _prepare_discord_media_payload(
        self,
        source_media,
        text="",
        video_url=None,
        status_link=None,
    ):
        """Build embeds and attachment files shared by post() and reply()."""
        self._require_api()

        embeds: List[Any] = []
        attachment_files: List[discord.File] = []
        cleanup_targets: List[Any] = []

        if status_link:
            scraped_data = parse_metatags(status_link)
            status_link_title = scraped_data.get("title", "")
            status_link_description = scraped_data.get("description", "")
            status_link_image = scraped_data.get("image", "")
            validate_discord_embeds([{"title": status_link_title, "description": status_link_description}])
            link_embed = self.api.create_embed(
                title=status_link_title,
                description=status_link_description,
                url=status_link,
                image_url=status_link_image,
            )
            embeds.append(link_embed)

        if source_media:
            await self._append_image_embeds(embeds, source_media, cleanup_targets, attachment_files)

        if video_url:
            text, file_obj = await self._prepare_video_file(embeds, cleanup_targets, video_url, "", text)
            if file_obj is not None:
                attachment_files.append(file_obj)

        return text, embeds, attachment_files, cleanup_targets

    async def post(
        self,
        status_text,
        status_link,
        status_image_url_1=None,
        status_image_url_2=None,
        status_image_url_3=None,
        status_image_url_4=None,
    ):
        """
        Create a post on Discord.

        Args:
            status_text (str): Text content of the post
            status_link (str): URL to include in the post
            status_image_url_1 (str, optional): First image URL
            status_image_url_2 (str, optional): Second image URL
            status_image_url_3 (str, optional): Third image URL
            status_image_url_4 (str, optional): Fourth image URL

        Returns:
            str: Post ID
        """
        self._require_api()

        source_media = self._collect_status_image_urls(
            status_image_url_1, status_image_url_2, status_image_url_3, status_image_url_4
        )

        if not source_media and not status_text and not status_link:
            raise Exception("No status text, link, or images provided.")

        validate_text("discord", "content", status_text or "")

        cleanup_targets: List[Any] = []
        try:
            content, embeds, attachment_files, cleanup_targets = await self._prepare_discord_media_payload(
                source_media, status_text or "", status_link=status_link
            )
            message_id = await self.api.post(
                content=content or None,
                embeds=embeds if embeds else None,
                files=attachment_files if attachment_files else None,
            )
        finally:
            for item in cleanup_targets:
                try:
                    item.cleanup()
                except Exception:
                    pass

        self._output_status(message_id)
        return message_id

    async def reply(
        self,
        post_id,
        text,
        status_image_url_1=None,
        status_image_url_2=None,
        status_image_url_3=None,
        status_image_url_4=None,
        video_url=None,
    ):
        """
        Reply to a Discord message with optional media.

        Args:
            post_id (str): ID of the message to reply to
            text (str): Reply text
            status_image_url_1 (str, optional): First image URL
            status_image_url_2 (str, optional): Second image URL
            status_image_url_3 (str, optional): Third image URL
            status_image_url_4 (str, optional): Fourth image URL
            video_url (str, optional): URL of a video to attach to the reply

        Returns:
            str: Reply message ID
        """
        self._require_api()

        if not post_id:
            raise Exception("Discord post ID is required for reply action.")

        source_media = self._collect_status_image_urls(
            status_image_url_1, status_image_url_2, status_image_url_3, status_image_url_4
        )

        if not source_media and not text and not video_url:
            raise Exception("No reply text or media provided.")

        validate_text("discord", "content", text or "")

        cleanup_targets: List[Any] = []
        try:
            content, embeds, attachment_files, cleanup_targets = await self._prepare_discord_media_payload(
                source_media, text or "", video_url=video_url
            )
            message_id = await self.api.reply(
                post_id,
                content=content or None,
                embeds=embeds if embeds else None,
                files=attachment_files if attachment_files else None,
            )
        finally:
            for item in cleanup_targets:
                try:
                    item.cleanup()
                except Exception:
                    pass

        self._output_status(message_id)
        return message_id

    async def _append_custom_embeds(self, embeds: List[Any], custom_embeds: List[Any]) -> None:
        self._require_api()
        for embed_data in custom_embeds:
            if not isinstance(embed_data, dict):
                raise Exception("Each embed must be a mapping.")
            embeds.append(
                self.api.create_embed(
                    title=embed_data.get("title"),
                    description=embed_data.get("description"),
                    url=embed_data.get("url"),
                    image_url=embed_data.get("image_url"),
                )
            )

    async def _append_link_embed(self, embeds: List[Any], link: str) -> None:
        self._require_api()
        scraped_data = parse_metatags(link)
        embeds.append(
            self.api.create_embed(
                title=scraped_data.get("title", ""),
                description=scraped_data.get("description", ""),
                url=link,
                image_url=scraped_data.get("image", ""),
            )
        )

    async def _append_image_embeds(
        self,
        embeds: List[Any],
        images: List[str],
        cleanup_targets: List[Any],
        attachment_files: List[discord.File],
    ) -> None:
        self._require_api()
        downloaded = await self.download_images(images)
        for image in downloaded:
            try:
                if media_is_local(image):
                    extension = image.file_type.extension if image.file_type else "bin"
                    attachment_files.append(discord.File(image.get_file_like_object(), filename=f"image.{extension}"))
                else:
                    embeds.append(self.api.create_embed(image_url=image.url))
            finally:
                cleanup_targets.append(image)

    async def _prepare_video_file(
        self,
        embeds: List[Any],
        cleanup_targets: List[Any],
        video_url: str,
        video_title: str,
        text: Optional[str],
    ):
        self._require_api()
        video = await self.download_video(video_url)
        cleanup_targets.append(video)
        if not video.content or not video.file_type:
            for item in cleanup_targets:
                try:
                    item.cleanup()
                except Exception:
                    pass
            raise Exception("Failed to download or validate video")
        content = text
        if video_title or text:
            embeds.append(self.api.create_embed(title=video_title or "Video", description=text or ""))
            content = None
        file_obj = video.get_file_like_object()
        file_obj = discord.File(file_obj, filename=f"video.{video.file_type.extension}")
        return content, file_obj

    async def _build_entry_payload(self, entry: Dict[str, Any]):
        """
        Build Discord content/embeds/file payload for one entry (no printing).

        Returns:
            tuple: (content, embeds, attachment_files, cleanup_callable)
        """
        self._require_api()

        text = entry.get("text") or None
        link = entry.get("link") or ""
        images = _entry_images(entry)
        video_url = entry.get("video_url")
        video_title = entry.get("video_title") or ""
        custom_embeds = entry.get("embeds") or []

        if images and video_url:
            raise Exception("Images and video_url are mutually exclusive in a thread entry.")

        embeds: List[Any] = []
        cleanup_targets: List[Any] = []
        attachment_files: List[discord.File] = []

        await self._append_custom_embeds(embeds, custom_embeds)
        if link:
            await self._append_link_embed(embeds, link)
        if images:
            await self._append_image_embeds(embeds, images, cleanup_targets, attachment_files)

        if video_url:
            text, file_obj = await self._prepare_video_file(embeds, cleanup_targets, video_url, video_title, text)
            if file_obj is not None:
                attachment_files.append(file_obj)

        def _cleanup():
            for item in cleanup_targets:
                try:
                    item.cleanup()
                except Exception:
                    pass

        return text, embeds if embeds else None, attachment_files, _cleanup

    def _prevalidate_entries(self, entries: List[Dict[str, Any]], thread_name: str) -> None:
        """Validate thread_name and every entry before any network publish."""
        validate_text("discord", "thread_name", thread_name)
        for entry in entries:
            if not isinstance(entry, dict):
                raise Exception("Each thread entry must be a mapping.")
            images = _entry_images(entry)
            video_url = entry.get("video_url")
            if images and video_url:
                raise Exception("Images and video_url are mutually exclusive in a thread entry.")
            text = entry.get("text")
            if text:
                validate_text("discord", "content", text)
            embeds = entry.get("embeds") or []
            if embeds:
                validate_discord_embeds(embeds)
            if not text and not entry.get("link") and not images and not video_url and not embeds:
                raise Exception("Thread entry requires text, link, images, video_url, or embeds.")

    async def thread(self, entries, **kwargs) -> ThreadResult:
        """
        Publish a public Discord text-channel thread from a starter message.

        Args:
            entries: Ordered entry mappings
            **kwargs: thread_name (required), auto_archive_duration (optional)

        Returns:
            ThreadResult: Structured success result including thread_id

        Raises:
            ThreadPublishError: On partial or failed publish with structured result
        """
        self._require_api()

        if not entries or not isinstance(entries, list):
            raise Exception("Thread entries are required.")

        thread_name = kwargs.get("thread_name")
        if not thread_name:
            raise Exception("thread_name is required for Discord thread publishing.")

        auto_archive_duration = kwargs.get("auto_archive_duration")
        if auto_archive_duration is not None:
            auto_archive_duration = int(auto_archive_duration)
            if auto_archive_duration not in _DISCORD_ARCHIVE_DURATIONS:
                raise Exception(f"auto_archive_duration must be one of {sorted(_DISCORD_ARCHIVE_DURATIONS)} minutes.")

        self._prevalidate_entries(entries, thread_name)

        ids: List[str] = []
        thread_id: Optional[str] = None

        # First entry → channel starter message
        cleanup = None
        try:
            content, embeds, attachment_files, cleanup = await self._build_entry_payload(entries[0])
            starter_id = await self.api.post(
                content=content,
                embeds=embeds,
                files=attachment_files if attachment_files else None,
            )
            ids.append(str(starter_id))
        except Exception as exc:
            outcome = "unknown" if _is_uncertain_publish_error(exc) else "failed"
            raise ThreadPublishError(partial_result(ids, failed_index=0, outcome=outcome, error=str(exc))) from exc
        finally:
            if cleanup:
                cleanup()

        # Create public thread from starter
        try:
            thread_id = await self.api.create_public_thread(
                ids[0], thread_name, auto_archive_duration=auto_archive_duration
            )
        except Exception as exc:
            outcome = "unknown" if _is_uncertain_publish_error(exc) else "failed"
            raise ThreadPublishError(
                partial_result(ids, failed_index=0, outcome=outcome, error=str(exc), thread_id=thread_id)
            ) from exc

        # Remaining entries → thread channel
        for index, entry in enumerate(entries[1:], start=1):
            cleanup = None
            try:
                content, embeds, attachment_files, cleanup = await self._build_entry_payload(entry)
                message_id = await self.api.send_message_to_thread(
                    thread_id,
                    content=content,
                    embeds=embeds,
                    files=attachment_files if attachment_files else None,
                )
                ids.append(str(message_id))
            except Exception as exc:
                outcome = "unknown" if _is_uncertain_publish_error(exc) else "failed"
                raise ThreadPublishError(
                    partial_result(
                        ids,
                        failed_index=index,
                        outcome=outcome,
                        error=str(exc),
                        thread_id=thread_id,
                    )
                ) from exc
            finally:
                if cleanup:
                    cleanup()

        return success_result(ids, thread_id=thread_id)

    async def like(self, discord_post_id):
        """
        Like a Discord message by adding a heart reaction.

        Args:
            discord_post_id (str): ID of the Discord message to like

        Returns:
            str: Post ID
        """
        self._require_api()

        if not discord_post_id:
            raise Exception("Discord post ID is required.")

        result = await self.api.like(discord_post_id, "❤️")
        self._output_status(result)
        return result

    async def delete(self, discord_post_id):
        """
        Delete a Discord message.

        Args:
            discord_post_id (str): ID of the Discord message to delete

        Returns:
            str: Post ID
        """
        self._require_api()

        if not discord_post_id:
            raise Exception("Discord post ID is required.")

        result = await self.api.delete(discord_post_id)
        self._output_status(result)
        return result

    async def get_post(self, post_id):
        """
        Read a Discord message by ID and return normalized content.

        Args:
            post_id (str): Message ID to read

        Returns:
            dict: Normalized content
        """
        self._require_api()

        if not post_id:
            raise Exception("Discord post ID is required.")
        message_id = post_id

        raw = await self.api.get_post(message_id)
        content = {
            "id": raw.get("id", message_id),
            "text": raw.get("text"),
            "media": raw.get("media") or [],
            "author": raw.get("author"),
            "created_at": raw.get("created_at"),
            "metadata": {},
        }
        self._output_content(content)
        return content

    async def list_posts(self, limit):
        """
        List recent messages in the configured channel and return normalized content.

        Args:
            limit (int): Maximum number of messages to return

        Returns:
            list: Normalized content dicts
        """
        self._require_api()

        if limit == 0:
            self._output_list([])
            return []

        raw_items = await self.api.list_posts(limit)
        items = []
        for raw in raw_items:
            items.append(
                {
                    "id": raw.get("id"),
                    "text": raw.get("text"),
                    "media": raw.get("media") or [],
                    "author": raw.get("author"),
                    "created_at": raw.get("created_at"),
                    "metadata": {},
                }
            )
        self._output_list(items)
        return items

    async def share(self, discord_post_id):
        """
        Share is not supported for Discord.

        Args:
            discord_post_id (str): ID of the Discord message

        Raises:
            Exception: Share not supported for Discord
        """
        raise Exception("Share not supported for Discord")

    async def video(self, status_text, video_url, video_title):
        """
        Post a video to Discord.

        Args:
            status_text (str): Text content to accompany the video
            video_url (str): URL of the video to post
            video_title (str): Title of the video

        Returns:
            str: Post ID
        """
        self._require_api()

        if not video_url:
            raise Exception("No Discord video URL provided.")

        # Validate embed text before media I/O when title/description are known
        if video_title or status_text:
            validate_discord_embeds([{"title": video_title or "Video", "description": status_text or ""}])

        # Download and validate video using the Media system
        video = await self.download_video(video_url)

        if not video.content or not video.file_type:
            video.cleanup()
            raise Exception("Failed to download or validate video")

        try:
            # Create embed for video title and description
            embeds = []
            if video_title or status_text:
                embed = self.api.create_embed(title=video_title or "Video", description=status_text)
                embeds.append(embed)

            # Get file-like object directly from video content in memory
            video_file = video.get_file_like_object()
            filename = f"video.{video.file_type.extension}"

            # Upload file using Discord API
            message_id = await self.api.upload_file(
                video_file, filename, content=None, embeds=embeds if embeds else None
            )

        finally:
            # Clean up
            video.cleanup()

        self._output_status(message_id)
        return message_id


async def main_async(kwargs):
    """
    Async main function to execute Discord actions.

    Thin shim: delegates to the base template runner via unbound dispatch,
    so test mocks of ``Discord`` (which stub ``execute_action``/``disconnect``/
    ``authorize_credentials`` but not the base method) keep working. The
    name is kept module-level because tests and the CLI import it.

    Args:
        kwargs (dict): Configuration arguments
    """
    instance = Discord(**kwargs)
    return await SocialNetwork.run_main_async(instance, kwargs)


def main(kwargs):
    """
    Main function to execute Discord actions (for backwards compatibility).

    Thin shim kept module-level because the CLI imports it.

    Args:
        kwargs (dict): Configuration arguments
    """
    asyncio.run(main_async(kwargs))
