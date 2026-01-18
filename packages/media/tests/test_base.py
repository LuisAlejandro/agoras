# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
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

import io
import os
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

import pytest

from agoras.media.base import Media
from agoras.media.image import Image


def test_media_is_abstract():
    """Test that Media cannot be instantiated directly."""
    with pytest.raises(TypeError):
        Media('https://example.com/file.jpg')


def test_media_url_attribute():
    """Test that Media subclasses have url attribute."""
    image = Image('https://example.com/test.jpg')
    assert image.url == 'https://example.com/test.jpg'
    assert image.temp_file is None
    assert image.content is None
    assert image._downloaded is False


def test_media_cleanup_method_exists():
    """Test that cleanup method exists in Media interface."""
    assert hasattr(Media, 'cleanup')
    assert callable(getattr(Media, 'cleanup'))


# Download and Validation Tests

@pytest.mark.asyncio
@patch('agoras.media.base.filetype.guess')
@patch('agoras.media.base.urlopen')
@patch('agoras.media.base.tempfile.mkstemp')
@patch('builtins.open', new_callable=mock_open)
async def test_download_success(mock_file, mock_mkstemp, mock_urlopen, mock_filetype):
    """Test successful download with mocked URL."""
    # Mock temp file creation
    mock_mkstemp.return_value = (1, '/tmp/test-image-123.bin')

    # Mock URL response
    mock_response = MagicMock()
    mock_response.read.return_value = b'fake_jpeg_data'
    mock_urlopen.return_value = mock_response

    # Mock file type validation
    mock_type = MagicMock()
    mock_type.mime = 'image/jpeg'
    mock_filetype.return_value = mock_type

    image = Image('https://example.com/test.jpg')
    temp_file, content, file_type = await image.download()

    assert image._downloaded is True
    assert image.content == b'fake_jpeg_data'
    assert image.temp_file == '/tmp/test-image-123.bin'
    assert temp_file == '/tmp/test-image-123.bin'
    assert content == b'fake_jpeg_data'


@pytest.mark.asyncio
@patch('agoras.media.base.filetype.guess')
@patch('agoras.media.base.urlopen')
@patch('agoras.media.base.tempfile.mkstemp')
@patch('builtins.open', new_callable=mock_open)
async def test_download_already_downloaded(mock_file, mock_mkstemp, mock_urlopen, mock_filetype):
    """Test that download returns cached data if already downloaded."""
    # Setup mocks
    mock_mkstemp.return_value = (1, '/tmp/test.bin')
    mock_response = MagicMock()
    mock_response.read.return_value = b'data'
    mock_urlopen.return_value = mock_response
    mock_type = MagicMock()
    mock_type.mime = 'image/jpeg'
    mock_filetype.return_value = mock_type

    image = Image('https://example.com/test.jpg')

    # First download
    await image.download()
    first_call_count = mock_urlopen.call_count

    # Second download should use cache
    await image.download()

    # Should not call urlopen again
    assert mock_urlopen.call_count == first_call_count


@pytest.mark.asyncio
@patch('agoras.media.base.filetype.guess')
@patch('agoras.media.base.urlopen')
@patch('agoras.media.base.tempfile.mkstemp')
@patch('builtins.open', new_callable=mock_open)
async def test_validate_file_type_invalid(mock_file, mock_mkstemp, mock_urlopen, mock_filetype):
    """Test file type validation failure with invalid type."""
    # Setup mocks
    mock_mkstemp.return_value = (1, '/tmp/test.bin')
    mock_response = MagicMock()
    mock_response.read.return_value = b'invalid_data'
    mock_urlopen.return_value = mock_response

    # Mock filetype returning None (unknown type)
    mock_filetype.return_value = None

    image = Image('https://example.com/test.jpg')

    with pytest.raises(Exception, match='Invalid image type'):
        await image.download()


@pytest.mark.asyncio
@patch('agoras.media.base.os.unlink')
@patch('agoras.media.base.os.path.exists', return_value=True)
@patch('agoras.media.base.filetype.guess')
@patch('agoras.media.base.urlopen')
@patch('agoras.media.base.tempfile.mkstemp')
@patch('builtins.open', new_callable=mock_open)
async def test_validate_file_type_disallowed(mock_file, mock_mkstemp, mock_urlopen,
                                             mock_filetype, mock_exists, mock_unlink):
    """Test file type validation failure with disallowed type."""
    # Setup mocks
    mock_mkstemp.return_value = (1, '/tmp/test.bin')
    mock_response = MagicMock()
    mock_response.read.return_value = b'pdf_data'
    mock_urlopen.return_value = mock_response

    # Mock filetype returning PDF (not allowed for images)
    mock_type = MagicMock()
    mock_type.mime = 'application/pdf'
    mock_filetype.return_value = mock_type

    image = Image('https://example.com/test.jpg')

    with pytest.raises(Exception, match='Invalid image type "application/pdf"'):
        await image.download()


# File Handle Tests

def test_get_file_handle_before_download():
    """Test get_file_handle raises exception before download."""
    image = Image('https://example.com/test.jpg')

    with pytest.raises(Exception, match='File must be downloaded'):
        image.get_file_handle()


@pytest.mark.asyncio
@patch('agoras.media.base.filetype.guess')
@patch('agoras.media.base.urlopen')
@patch('agoras.media.base.tempfile.mkstemp')
@patch('builtins.open', new_callable=mock_open)
async def test_get_file_handle_after_download(mock_file, mock_mkstemp, mock_urlopen, mock_filetype):
    """Test get_file_handle returns BytesIO after download."""
    # Setup mocks
    mock_mkstemp.return_value = (1, '/tmp/test.bin')
    mock_response = MagicMock()
    mock_response.read.return_value = b'image_data'
    mock_urlopen.return_value = mock_response
    mock_type = MagicMock()
    mock_type.mime = 'image/jpeg'
    mock_filetype.return_value = mock_type

    image = Image('https://example.com/test.jpg')
    await image.download()

    handle = image.get_file_handle()

    assert isinstance(handle, io.BytesIO)
    assert handle.read() == b'image_data'


def test_get_file_like_object_before_download():
    """Test get_file_like_object raises exception before download."""
    image = Image('https://example.com/test.jpg')

    with pytest.raises(Exception, match='File must be downloaded'):
        image.get_file_like_object()


@pytest.mark.asyncio
@patch('agoras.media.base.filetype.guess')
@patch('agoras.media.base.urlopen')
@patch('agoras.media.base.tempfile.mkstemp')
@patch('builtins.open', new_callable=mock_open)
async def test_get_file_like_object_after_download(mock_file, mock_mkstemp, mock_urlopen, mock_filetype):
    """Test get_file_like_object returns BytesIO after download."""
    # Setup mocks
    mock_mkstemp.return_value = (1, '/tmp/test.bin')
    mock_response = MagicMock()
    mock_response.read.return_value = b'image_content'
    mock_urlopen.return_value = mock_response
    mock_type = MagicMock()
    mock_type.mime = 'image/png'
    mock_filetype.return_value = mock_type

    image = Image('https://example.com/test.jpg')
    await image.download()

    file_obj = image.get_file_like_object()

    assert isinstance(file_obj, io.BytesIO)
    assert file_obj.read() == b'image_content'


# File Size Tests

def test_get_file_size_before_download():
    """Test get_file_size raises exception before download."""
    image = Image('https://example.com/test.jpg')

    with pytest.raises(Exception, match='File must be downloaded'):
        image.get_file_size()


@pytest.mark.asyncio
@patch('agoras.media.base.filetype.guess')
@patch('agoras.media.base.urlopen')
@patch('agoras.media.base.tempfile.mkstemp')
@patch('builtins.open', new_callable=mock_open)
async def test_get_file_size_after_download(mock_file, mock_mkstemp, mock_urlopen, mock_filetype):
    """Test get_file_size returns correct size after download."""
    # Setup mocks
    mock_mkstemp.return_value = (1, '/tmp/test.bin')
    test_data = b'x' * 1024  # 1 KB of data
    mock_response = MagicMock()
    mock_response.read.return_value = test_data
    mock_urlopen.return_value = mock_response
    mock_type = MagicMock()
    mock_type.mime = 'image/jpeg'
    mock_filetype.return_value = mock_type

    image = Image('https://example.com/test.jpg')
    await image.download()

    size = image.get_file_size()

    assert size == 1024


# Cleanup Tests

@patch('agoras.media.base.os.unlink')
@patch('agoras.media.base.os.path.exists', return_value=True)
def test_cleanup_removes_temp_file(mock_exists, mock_unlink):
    """Test cleanup removes temp file."""
    image = Image('https://example.com/test.jpg')
    image.temp_file = '/tmp/test-file.bin'
    image.content = b'data'
    image._downloaded = True

    image.cleanup()

    mock_unlink.assert_called_once_with('/tmp/test-file.bin')
    assert image.temp_file is None
    assert image.content is None
    assert image._downloaded is False


@patch('agoras.media.base.os.unlink')
@patch('agoras.media.base.os.path.exists', return_value=False)
def test_cleanup_handles_missing_file(mock_exists, mock_unlink):
    """Test cleanup handles missing file gracefully."""
    image = Image('https://example.com/test.jpg')
    image.temp_file = '/tmp/nonexistent.bin'
    image.content = b'data'
    image._downloaded = True

    # Should not raise exception
    image.cleanup()

    mock_unlink.assert_not_called()
    # Cleanup still resets attributes even if file doesn't exist
    assert image.content is None
    assert image._downloaded is False


def test_cleanup_closes_file_handles():
    """Test cleanup closes file handles."""
    image = Image('https://example.com/test.jpg')

    # Create a mock file handle
    mock_handle = MagicMock()
    image._file_handle = mock_handle

    image.cleanup()

    mock_handle.close.assert_called_once()
    assert image._file_handle is None


@patch('agoras.media.base.os.unlink')
@patch('agoras.media.base.os.path.exists', return_value=True)
def test_cleanup_handles_close_exception(mock_exists, mock_unlink):
    """Test cleanup handles file close exceptions gracefully."""
    image = Image('https://example.com/test.jpg')
    image.temp_file = '/tmp/test.bin'

    # Create a mock file handle that raises on close
    mock_handle = MagicMock()
    mock_handle.close.side_effect = Exception('Close failed')
    image._file_handle = mock_handle

    # Should not raise exception
    image.cleanup()

    assert image._file_handle is None


# Context Manager Tests

@patch('agoras.media.base.os.unlink')
@patch('agoras.media.base.os.path.exists', return_value=True)
def test_context_manager_sync(mock_exists, mock_unlink):
    """Test sync context manager calls cleanup on exit."""
    with Image('https://example.com/test.jpg') as image:
        image.temp_file = '/tmp/test.bin'
        image._downloaded = True

    # Cleanup should have been called
    mock_unlink.assert_called_once()


@pytest.mark.asyncio
@patch('agoras.media.base.os.unlink')
@patch('agoras.media.base.os.path.exists', return_value=True)
async def test_context_manager_async(mock_exists, mock_unlink):
    """Test async context manager calls cleanup on exit."""
    async with Image('https://example.com/test.jpg') as image:
        image.temp_file = '/tmp/test.bin'
        image._downloaded = True

    # Cleanup should have been called
    mock_unlink.assert_called_once()


@patch('agoras.media.base.os.unlink')
@patch('agoras.media.base.os.path.exists', return_value=True)
def test_context_manager_cleanup_on_exception(mock_exists, mock_unlink):
    """Test context manager calls cleanup even on exception."""
    try:
        with Image('https://example.com/test.jpg') as image:
            image.temp_file = '/tmp/test.bin'
            raise ValueError('Test exception')
    except ValueError:
        pass

    # Cleanup should still have been called
    mock_unlink.assert_called_once()


def test_get_file_prefix():
    """Test _get_file_prefix returns correct prefix."""
    image = Image('https://example.com/test.jpg')
    prefix = image._get_file_prefix()

    assert prefix == 'image-'
