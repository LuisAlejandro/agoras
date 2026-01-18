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

import doctest
import io
import logging
import os
import sys
import tempfile
import unittest

from agoras.common.logger import levelNames, logger


class TestLogger(unittest.TestCase):

    def setUp(self):
        # Ensure logger is stopped before each test
        if not logger.disabled:
            logger.stop()

    def tearDown(self):
        # Clean up after each test
        if not logger.disabled:
            logger.stop()

    def test_01_default_level(self):
        """Test logger default state."""
        # Logger should be disabled initially
        self.assertTrue(logger.disabled)

    def test_start_without_filename(self):
        """Test starting logger without filename parameter."""
        logger.start()

        # Logger should be enabled
        self.assertFalse(logger.disabled)

        # Should have exactly one handler (StreamHandler)
        self.assertEqual(len(logger.handlers), 1)
        self.assertIsInstance(logger.handlers[0], logging.StreamHandler)

    def test_start_with_filename(self):
        """Test starting logger with filename parameter."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_filename = f.name

        try:
            logger.start(filename=temp_filename)

            # Logger should be enabled
            self.assertFalse(logger.disabled)

            # Should have two handlers (StreamHandler + FileHandler)
            self.assertEqual(len(logger.handlers), 2)

            # Check handler types
            handler_types = [type(h).__name__ for h in logger.handlers]
            self.assertIn('StreamHandler', handler_types)
            self.assertIn('FileHandler', handler_types)

            logger.stop()
        finally:
            # Clean up temp file
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    def test_start_when_already_started(self):
        """Test that starting an already started logger doesn't add duplicate handlers."""
        logger.start()
        initial_handler_count = len(logger.handlers)

        # Try to start again
        logger.start()

        # Handler count should not increase
        self.assertEqual(len(logger.handlers), initial_handler_count)

    def test_stop_after_start(self):
        """Test stopping logger after starting."""
        logger.start()
        self.assertFalse(logger.disabled)
        self.assertGreater(len(logger.handlers), 0)

        logger.stop()

        # Logger should be disabled
        self.assertTrue(logger.disabled)

        # All handlers should be removed
        self.assertEqual(len(logger.handlers), 0)

    def test_stop_when_already_stopped(self):
        """Test stopping an already stopped logger."""
        # Ensure logger is stopped
        if not logger.disabled:
            logger.stop()

        # Should not raise error
        logger.stop()

        # Should still be disabled
        self.assertTrue(logger.disabled)

    def test_stop_clears_all_handlers(self):
        """Test that stop clears all handlers including file handler."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_filename = f.name

        try:
            logger.start(filename=temp_filename)
            self.assertEqual(len(logger.handlers), 2)

            logger.stop()

            # All handlers should be cleared
            self.assertEqual(len(logger.handlers), 0)
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    def test_loglevel_sets_debug(self):
        """Test setting log level to DEBUG."""
        logger.start()
        logger.loglevel('DEBUG')

        self.assertEqual(logger.level, 10)

        logger.stop()

    def test_loglevel_sets_info(self):
        """Test setting log level to INFO."""
        logger.start()
        logger.loglevel('INFO')

        self.assertEqual(logger.level, 20)

        logger.stop()

    def test_loglevel_sets_warning(self):
        """Test setting log level to WARNING."""
        logger.start()
        logger.loglevel('WARNING')

        self.assertEqual(logger.level, 30)

        logger.stop()

    def test_loglevel_sets_error(self):
        """Test setting log level to ERROR."""
        logger.start()
        logger.loglevel('ERROR')

        self.assertEqual(logger.level, 40)

        logger.stop()

    def test_loglevel_sets_critical(self):
        """Test setting log level to CRITICAL."""
        logger.start()
        logger.loglevel('CRITICAL')

        self.assertEqual(logger.level, 50)

        logger.stop()

    def test_loglevel_sets_notset(self):
        """Test setting log level to NOTSET."""
        logger.start()
        logger.loglevel('NOTSET')

        self.assertEqual(logger.level, 0)

        logger.stop()

    def test_loglevel_on_disabled_logger(self):
        """Test that loglevel has no effect on disabled logger."""
        # Ensure logger is disabled
        if not logger.disabled:
            logger.stop()

        initial_level = logger.level

        # Try to set level on disabled logger
        logger.loglevel('DEBUG')

        # Level should not change
        self.assertEqual(logger.level, initial_level)

    def test_logger_format_string(self):
        """Test that logger uses correct format string."""
        self.assertEqual(logger.formatstring, '[%(levelname)s] %(message)s')

    def test_logger_actually_logs_messages(self):
        """Test that logger actually outputs log messages."""
        # Create a string buffer to capture output
        string_buffer = io.StringIO()

        # Create a handler that writes to our buffer
        handler = logging.StreamHandler(string_buffer)
        handler.setFormatter(logging.Formatter(logger.formatstring))

        # Manually add handler (simulating start behavior)
        logger.addHandler(handler)
        logger.disabled = False
        logger.setLevel(logging.INFO)

        # Log a message
        logger.info('Test message')

        # Get output
        output = string_buffer.getvalue()

        # Verify message appears with correct format
        self.assertIn('[INFO] Test message', output)

        # Clean up
        logger.removeHandler(handler)
        logger.disabled = True


def load_tests(loader, tests, pattern):
    tests.addTests(doctest.DocTestSuite('agoras.common.logger'))
    return tests


if __name__ == '__main__':
    sys.exit(unittest.main())
