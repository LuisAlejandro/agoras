# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
# Copyright (C) 2022-2023, Agoras Developers.

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

import asyncio
import io
import os
import tempfile
from abc import ABC, abstractmethod
from urllib.request import Request, urlopen

import filetype

from agoras.common import __version__


class Media(ABC):
    """
    Abstract base class for media handling.

    Provides common functionality for downloading, validating, and managing
    media files from URLs.
    """

    def __init__(self, url):
        """
        Initialize media instance.

        Args:
            url (str): URL of the media to download
        """
        self.url = url
        self.temp_file = None
        self.content = None
        self.file_type = None
        self._downloaded = False
        self._file_handle = None

    @property
    @abstractmethod
    def allowed_types(self):
        """
        Get list of allowed MIME types for this media type.

        Returns:
            list: List of allowed MIME types
        """

    async def download(self):
        """
        Download media from URL asynchronously.

        Returns:
            tuple: (temp_file_path, content, file_type)

        Raises:
            Exception: If download or validation fails
        """
        if self._downloaded:
            return self.temp_file, self.content, self.file_type

        def _sync_download():
            _, tmpfile = tempfile.mkstemp(prefix=self._get_file_prefix(), suffix='.bin')

            with open(tmpfile, 'wb') as f:
                request = Request(url=self.url, headers={'User-Agent': f'Agoras/{__version__}'})
                content = urlopen(request).read()
                f.write(content)

            return tmpfile, content

        self.temp_file, self.content = await asyncio.to_thread(_sync_download)
        self.file_type = self._validate_file_type()
        self._validate_content()
        self._downloaded = True

        return self.temp_file, self.content, self.file_type

    def get_file_handle(self, mode='rb'):
        """
        Get a file handle for the downloaded content.

        Args:
            mode (str): File open mode (default: 'rb')

        Returns:
            io.BytesIO or file handle: File handle for the content

        Raises:
            Exception: If file hasn't been downloaded
        """
        if not self._downloaded:
            raise Exception('File must be downloaded before getting file handle')

        if self.content is not None:
            # Return BytesIO handle from in-memory content
            return io.BytesIO(self.content)
        elif self.temp_file and os.path.exists(self.temp_file):
            # Fallback to file handle if content not in memory
            return open(self.temp_file, mode)
        else:
            raise Exception('No file content available')

    def get_file_like_object(self):
        """
        Get a file-like object that can be used with libraries expecting file handles.

        Returns:
            io.BytesIO: File-like object containing the media content

        Raises:
            Exception: If file hasn't been downloaded
        """
        if not self._downloaded:
            raise Exception('File must be downloaded before getting file object')

        if self.content is not None:
            return io.BytesIO(self.content)
        else:
            raise Exception('No file content available in memory')

    def _get_file_prefix(self):
        """
        Get file prefix for temporary files.

        Returns:
            str: File prefix
        """
        return f'{self.__class__.__name__.lower()}-'

    def _validate_file_type(self):
        """
        Validate file type and return file type info.

        Returns:
            FileType: File type information

        Raises:
            Exception: If file type is invalid
        """
        if not self.temp_file:
            raise Exception('File must be downloaded before validation')

        kind = filetype.guess(self.temp_file)

        if not kind:
            self.cleanup()
            raise Exception(f'Invalid {self.__class__.__name__.lower()} type for {self.url}')

        if kind.mime not in self.allowed_types:
            self.cleanup()
            media_type = self.__class__.__name__.lower()
            raise Exception(f'Invalid {media_type} type "{kind.mime}" for {self.url}. '
                            f'Allowed types: {self.allowed_types}')

        return kind

    def _validate_content(self):
        """
        Validate media content. Override in subclasses for specific validation.
        """

    def get_file_size(self):
        """
        Get file size in bytes.

        Returns:
            int: File size in bytes

        Raises:
            Exception: If file hasn't been downloaded
        """
        if not self._downloaded:
            raise Exception('File must be downloaded before getting size')

        if self.content is not None:
            return len(self.content)
        elif self.temp_file:
            return os.path.getsize(self.temp_file)
        else:
            raise Exception('No file content available')

    def cleanup(self):
        """
        Clean up temporary files and file handles.
        """
        if self._file_handle:
            try:
                self._file_handle.close()
            except Exception:
                pass
            self._file_handle = None

        if self.temp_file and os.path.exists(self.temp_file):
            try:
                os.unlink(self.temp_file)
            except Exception:
                pass
            self.temp_file = None

        self.content = None
        self.file_type = None
        self._downloaded = False

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with automatic cleanup."""
        self.cleanup()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with automatic cleanup."""
        self.cleanup()
