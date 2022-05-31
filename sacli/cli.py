# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
# Copyright (C) 2016-2022, Social Actions CLI Developers.

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
``sacli.cli`` is a module for handling the command line interface.

This module handles the commands for using sacli. It also parses
parameters, show help, version and controls the logging level.
"""

import re
import sys
from argparse import ArgumentParser

from . import __version__, __description__
from .core.logger import logger
from .api.publish import main as publish


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
        prog='sacli', description=__description__, add_help=False,
        usage='\t%(prog)s [options]\n\t%(prog)s <command> [options]')
    gen_options = parser.add_argument_group('General Options')
    gen_options.add_argument(
        '-V', '--version', action='version',
        version='sacli {0}'.format(__version__),
        help='Print version and exit.')
    gen_options.add_argument(
        '-h', '--help', action='help', help='Show this help message and exit.')
    subparsers = parser.add_subparsers(title='Commands', metavar='')

    publish_parser = subparsers.add_parser(
        'publish', prog='sacli', usage='%(prog)s publish [options]',
        help='Publish posts to different social networks', add_help=False)
    publish_parser.set_defaults(command=publish)
    publish_gen_options = publish_parser.add_argument_group('General Options')
    publish_gen_options.add_argument(
        '-V', '--version', action='version',
        version='sacli {0}'.format(__version__),
        help='Print version and exit.')
    publish_gen_options.add_argument(
        '-h', '--help', action='help', help='Show this help message and exit.')

    publish_options = publish_parser.add_argument_group('Publish Options')
    publish_options.add_argument(
        '-l', '--loglevel', default='INFO', metavar='<level>',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help=('Logger verbosity level (default: INFO). Must be one of: '
              'DEBUG, INFO, WARNING, ERROR or CRITICAL.'))
    publish_options.add_argument(
        '-n', '--network', default='', metavar='<social network>',
        choices=['twitter', 'facebook', 'instagram', 'linkedin'],
        help=('Social network to use for publishing (default: ""). '
              'Must be one of: '
              'twitter, facebook, instagram or linkedin.'))
    publish_options.add_argument(
        '-a', '--action', default='', metavar='<action>',
        choices=['like', 'share', 'last-from-feed', 'random-from-feed',
                 'schedule', 'post'],
        help=('Action to execute (default: ""). '
              'Must be one of: '
              'like, share, last-from-feed, random-from-feed'
              'schedule, post'))
    publish_options.add_argument(
        '-tk', '--twitter-consumer-key', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-ts', '--twitter-consumer-secret', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-tot', '--twitter-oauth-token', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-tos', '--twitter-oauth-secret', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-ft', '--facebook-access-token', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-fo', '--facebook-object-id', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-fp', '--facebook-post-id', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-it', '--instagram-access-token', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-io', '--instagram-object-id', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-ip', '--instagram-post-id', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-st', '--status-text', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-i1', '--status-image-url-1', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-i2', '--status-image-url-2', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-i3', '--status-image-url-3', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-i4', '--status-image-url-4', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-fu', '--feed-url', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-mc', '--max-count', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-pl', '--post-lookback', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-ma', '--max-post-age', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-ge', '--google-sheets-client-email', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-gi', '--google-sheets-id', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-gn', '--google-sheets-name', metavar='<>',
        help=(''))
    publish_options.add_argument(
        '-gk', '--google-sheets-private-key', metavar='<>',
        help=(''))

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
        status = args.command(**vars(args))
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
