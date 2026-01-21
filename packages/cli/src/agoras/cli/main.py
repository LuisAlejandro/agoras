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
"""
``agoras.cli`` is a module for handling the command line interface.

This module handles the commands for using agoras. It also parses
parameters, show help, version and controls the logging level.
"""

import re
import sys
from argparse import ArgumentParser

from agoras.common.logger import logger
from agoras.common.version import __description__, __version__

from .legacy import create_legacy_publish_parser
from .platforms.discord import create_discord_parser
from .platforms.facebook import create_facebook_parser
from .platforms.instagram import create_instagram_parser
from .platforms.linkedin import create_linkedin_parser
from .platforms.telegram import create_telegram_parser
from .platforms.threads import create_threads_parser
from .platforms.tiktok import create_tiktok_parser
from .platforms.whatsapp import create_whatsapp_parser
from .platforms.x import create_twitter_parser_alias, create_x_parser
from .platforms.youtube import create_youtube_parser
from .utils import create_utils_parser


def commandline(argv=None):
    """
    Configure ``ArgumentParser`` to accept custom arguments and commands.

    :param argv: a list of commandline arguments like ``sys.argv``.
                 For example::

                    ['-v', '--loglevel', 'INFO']

    :return: a ``Namespace`` object.

    .. versionadded:: 0.1.0
    """
    assert isinstance(argv, (list, type(None)))

    parser = ArgumentParser(
        prog='agoras', description=__description__, add_help=False,
        usage='\t%(prog)s [options]\n\t%(prog)s <command> [options]')
    gen_options = parser.add_argument_group('General Options')
    gen_options.add_argument(
        '-V', '--version', action='version',
        version='agoras {0}'.format(__version__),
        help='Print version and exit.')
    gen_options.add_argument(
        '-h', '--help', action='help', help='Show this help message and exit.')
    gen_options.add_argument(
        '-l', '--loglevel', default='INFO', metavar='<level>',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help=('Logger verbosity level (default: INFO). Must be one of: '
              'DEBUG, INFO, WARNING, ERROR or CRITICAL.'))

    # Create subparsers for commands
    subparsers = parser.add_subparsers(title='Commands', metavar='')

    # Register all platform commands
    create_x_parser(subparsers)
    create_twitter_parser_alias(subparsers)  # Deprecated alias for backward compatibility
    create_facebook_parser(subparsers)
    create_instagram_parser(subparsers)
    create_linkedin_parser(subparsers)
    create_discord_parser(subparsers)
    create_telegram_parser(subparsers)
    create_whatsapp_parser(subparsers)
    create_youtube_parser(subparsers)
    create_tiktok_parser(subparsers)
    create_threads_parser(subparsers)

    # Register utils command group (automation tools)
    create_utils_parser(subparsers)

    # Register legacy publish command
    create_legacy_publish_parser(subparsers, __version__)

    return parser, parser.parse_args(argv)


def main(argv=None):
    """
    Handle arguments and commands.

    :param argv: a list of commandline arguments like ``sys.argv``.
                 For example::

                    ['-v', '--loglevel', 'INFO']

    :return: an exit status.

    .. versionadded:: 0.1.0
    """
    assert isinstance(argv, (list, type(None)))

    parser, args = commandline(argv)

    if not hasattr(args, 'command'):
        parser.print_help()
        return 0

    logger.start()
    logger.loglevel(args.loglevel)
    logger.debug('Starting execution.')

    try:
        # Call handler with args Namespace
        # Handlers expect a single args argument, not unpacked kwargs
        status = args.command(args)
    except KeyboardInterrupt:
        logger.critical('Execution interrupted by user!')
        status = 1
    except Exception as e:
        logger.exception(e)
        logger.critical('Shutting down due to fatal error!')
        status = 1
    else:
        logger.debug('Ending execution.')

    logger.stop()
    return status


if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
