# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.rst for a complete list of Copyright holders.
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
"""
``agoras.cli`` is a module for handling the command line interface.

This module handles the commands for using agoras. It also parses
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
        prog='agoras', description=__description__, add_help=False,
        usage='\t%(prog)s [options]\n\t%(prog)s <command> [options]')
    gen_options = parser.add_argument_group('General Options')
    gen_options.add_argument(
        '-V', '--version', action='version',
        version='agoras {0}'.format(__version__),
        help='Print version and exit.')
    gen_options.add_argument(
        '-h', '--help', action='help', help='Show this help message and exit.')
    subparsers = parser.add_subparsers(title='Commands', metavar='')

    publish_parser = subparsers.add_parser(
        'publish', prog='agoras', usage='%(prog)s publish [options]',
        help='Publish posts to different social networks', add_help=False)
    publish_parser.set_defaults(command=publish)
    publish_gen_options = publish_parser.add_argument_group('General Options')
    publish_gen_options.add_argument(
        '-V', '--version', action='version',
        version='agoras {0}'.format(__version__),
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
                 'schedule', 'post', 'delete'],
        help=('Action to execute (default: ""). '
              'Must be one of: '
              'like, share, last-from-feed, random-from-feed, '
              'schedule, post, delete'))
    publish_options.add_argument(
        '-tk', '--twitter-consumer-key', metavar='<consumer key>',
        help=('Twitter consumer key from twitter developer app.'))
    publish_options.add_argument(
        '-ts', '--twitter-consumer-secret', metavar='<consumer secret>',
        help=('Twitter consumer secret from twitter developer app.'))
    publish_options.add_argument(
        '-tot', '--twitter-oauth-token', metavar='<oauth token>',
        help=('Twitter OAuth token from twitter developer app.'))
    publish_options.add_argument(
        '-tos', '--twitter-oauth-secret', metavar='<oauth secret>',
        help=('Twitter OAuth secret from twitter developer app.'))
    publish_options.add_argument(
        '-ti', '--tweet-id', metavar='<id>',
        help=('Twitter post ID to like, share or delete.'))
    publish_options.add_argument(
        '-ft', '--facebook-access-token', metavar='<access token>',
        help=('Facebook access token from facebook app.'))
    publish_options.add_argument(
        '-fo', '--facebook-object-id', metavar='<id>',
        help=('Facebook ID of object where the post is going '
              'to be published.'))
    publish_options.add_argument(
        '-fp', '--facebook-post-id', metavar='<id>',
        help=('Facebook ID of post to be liked, shared or deleted.'))
    publish_options.add_argument(
        '-fr', '--facebook-profile-id', metavar='<id>',
        help=('Facebook ID of profile where a post will be shared.'))
    publish_options.add_argument(
        '-it', '--instagram-access-token', metavar='<access token>',
        help=('Facebook access token from facebook app.'))
    publish_options.add_argument(
        '-io', '--instagram-object-id', metavar='<id>',
        help=('Instagram ID of profile where the post is going '
              'to be published.'))
    publish_options.add_argument(
        '-ip', '--instagram-post-id', metavar='<id>',
        help=('Instagram ID of post to be liked, shared or deleted.'))
    publish_options.add_argument(
        '-lw', '--linkedin-access-token', metavar='<access token>',
        help=('Your LinkedIn access token.'))
    publish_options.add_argument(
        '-lp', '--linkedin-post-id', metavar='<id>',
        help=('LinkedIn post ID to like, share or delete.'))
    publish_options.add_argument(
        '-st', '--status-text', metavar='<text>',
        help=('Text to be published.'))
    publish_options.add_argument(
        '-sl', '--status-link', metavar='<link>',
        help=('Link to be published.'))
    publish_options.add_argument(
        '-i1', '--status-image-url-1', metavar='<image url>',
        help=('First image URL to be published.'))
    publish_options.add_argument(
        '-i2', '--status-image-url-2', metavar='<image url>',
        help=('Second image URL to be published.'))
    publish_options.add_argument(
        '-i3', '--status-image-url-3', metavar='<image url>',
        help=('Third image URL to be published.'))
    publish_options.add_argument(
        '-i4', '--status-image-url-4', metavar='<image url>',
        help=('Fourth image URL to be published.'))
    publish_options.add_argument(
        '-fu', '--feed-url', metavar='<feed url>',
        help=('URL of public Atom feed to be parsed.'))
    publish_options.add_argument(
        '-mc', '--max-count', metavar='<number>',
        help=('Max number of new posts to be published at once.'))
    publish_options.add_argument(
        '-pl', '--post-lookback', metavar='<seconds>',
        help=('Only allow posts published '))
    publish_options.add_argument(
        '-ma', '--max-post-age', metavar='<days>',
        help=('Dont allow publishing of posts older than this '
              'number of days.'))
    publish_options.add_argument(
        '-ge', '--google-sheets-client-email', metavar='<email>',
        help=('A google console project client email corresponding'
              ' to the private key.'))
    publish_options.add_argument(
        '-gk', '--google-sheets-private-key', metavar='<private key>',
        help=('A google console project private key.'))
    publish_options.add_argument(
        '-gi', '--google-sheets-id', metavar='<id>',
        help=('The google sheets ID to read schedule entries.'))
    publish_options.add_argument(
        '-gn', '--google-sheets-name', metavar='<name>',
        help=('The name of the sheet where the schedule is.'))

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
