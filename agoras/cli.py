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
from .commands.publish import main as publish


def add_twitter_options(parser):
    parser.add_argument(
        '-tk', '--twitter-consumer-key', metavar='<consumer key>',
        help=('Twitter consumer key from twitter developer app.'))
    parser.add_argument(
        '-ts', '--twitter-consumer-secret', metavar='<consumer secret>',
        help=('Twitter consumer secret from twitter developer app.'))
    parser.add_argument(
        '-tot', '--twitter-oauth-token', metavar='<oauth token>',
        help=('Twitter OAuth token from twitter developer app.'))
    parser.add_argument(
        '-tos', '--twitter-oauth-secret', metavar='<oauth secret>',
        help=('Twitter OAuth secret from twitter developer app.'))
    parser.add_argument(
        '-ti', '--tweet-id', metavar='<id>',
        help=('Twitter post ID to like, share or delete.'))
    parser.add_argument(
        '-tvu', '--twitter-video-url', metavar='<video url>',
        help=('Twitter video file URL.'))
    parser.add_argument(
        '-tvt', '--twitter-video-title', metavar='<title>',
        help=('Twitter video title.'))


def add_facebook_options(parser):
    parser.add_argument(
        '-ft', '--facebook-access-token', metavar='<access token>',
        help=('Facebook access token from facebook app.'))
    parser.add_argument(
        '-fo', '--facebook-object-id', metavar='<id>',
        help=('Facebook ID of object where the post is going '
              'to be published.'))
    parser.add_argument(
        '-fp', '--facebook-post-id', metavar='<id>',
        help=('Facebook ID of post to be liked, shared or deleted.'))
    parser.add_argument(
        '-fr', '--facebook-profile-id', metavar='<id>',
        help=('Facebook ID of profile where a post will be shared.'))
    parser.add_argument(
        '-fa', '--facebook-app-id', metavar='<id>',
        help=('Facebook ID of profile where a post will be shared.'))
    parser.add_argument(
        '-fvu', '--facebook-video-url', metavar='<id>',
        help=('Facebook ID of profile where a post will be shared.'))
    parser.add_argument(
        '-fvt', '--facebook-video-type', metavar='<id>',
        help=('Facebook ID of profile where a post will be shared.'))
    parser.add_argument(
        '-fvi', '--facebook-video-title', metavar='<id>',
        help=('Facebook ID of profile where a post will be shared.'))
    parser.add_argument(
        '-fvd', '--facebook-video-description', metavar='<id>',
        help=('Facebook ID of profile where a post will be shared.'))


def add_discord_options(parser):
    parser.add_argument(
        '-dt', '--discord-bot-token', metavar='<bot token>',
        help=('Discord bot token.'))
    parser.add_argument(
        '-ds', '--discord-server-name', metavar='<name>',
        help=('Discord server name.'))
    parser.add_argument(
        '-dc', '--discord-channel-name', metavar='<name>',
        help=('Discord channel name.'))
    parser.add_argument(
        '-dp', '--discord-post-id', metavar='<id>',
        help=('Discord ID of post to be liked or deleted.'))
    parser.add_argument(
        '-dvu', '--discord-video-url', metavar='<video url>',
        help=('Discord video file URL.'))
    parser.add_argument(
        '-dvt', '--discord-video-title', metavar='<title>',
        help=('Discord video title.'))


def add_youtube_options(parser):
    parser.add_argument(
        '-yc', '--youtube-client-id', metavar='<name>',
        help=('YouTube client ID.'))
    parser.add_argument(
        '-ys', '--youtube-client-secret', metavar='<name>',
        help=('YouTube client secret.'))
    parser.add_argument(
        '-yi', '--youtube-video-id', metavar='<name>',
        help=('YouTube video ID to be liked or deleted.'))
    parser.add_argument(
        '-yt', '--youtube-title', metavar='<name>',
        help=('YouTube video title.'))
    parser.add_argument(
        '-yd', '--youtube-description', metavar='<name>',
        help=('YouTube video description.'))
    parser.add_argument(
        '-yr', '--youtube-category-id', metavar='<name>',
        help=('YouTube video category ID.'))
    parser.add_argument(
        '-yy', '--youtube-privacy-status', default='private', metavar='<name>',
        choices=["public", "private", "unlisted"],
        help=('YouTube video privacy status.'))
    parser.add_argument(
        '-yv', '--youtube-video-url', metavar='<video url>',
        help=('YouTube video file URL.'))
    parser.add_argument(
        '-yk', '--youtube-keywords', metavar='<name>',
        help=('YouTube video keywords separated by comma.'))


def add_google_sheets_options(parser):
    parser.add_argument(
        '-ge', '--google-sheets-client-email', metavar='<email>',
        help=('A google console project client email corresponding'
              ' to the private key.'))
    parser.add_argument(
        '-gk', '--google-sheets-private-key', metavar='<private key>',
        help=('A google console project private key.'))
    parser.add_argument(
        '-gi', '--google-sheets-id', metavar='<id>',
        help=('The google sheets ID to read schedule entries.'))
    parser.add_argument(
        '-gn', '--google-sheets-name', metavar='<name>',
        help=('The name of the sheet where the schedule is.'))


def add_tiktok_options(parser):
    parser.add_argument(
        '-tu', '--tiktok-username', metavar='<username>',
        help=('TikTok username.'))
    parser.add_argument(
        '-ta', '--tiktok-access-token', metavar='<access token>',
        help=('TikTok access token from authorize action.'))
    parser.add_argument(
        '-tr', '--tiktok-refresh-token', metavar='<refresh token>',
        help=('TikTok refresh token from authorize action.'))
    parser.add_argument(
        '-tck', '--tiktok-client-key', metavar='<client key>',
        help=('TikTok client key from developer app.'))
    parser.add_argument(
        '-tcs', '--tiktok-client-secret', metavar='<client secret>',
        help=('TikTok client secret from developer app.'))
    parser.add_argument(
        '-ty', '--tiktok-privacy-status', default='SELF_ONLY', metavar='<name>',
        choices=["PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "FOLLOWER_OF_CREATOR", "SELF_ONLY"],
        help=('TikTok video privacy status.'))
    parser.add_argument(
        '-tv', '--tiktok-video-url', metavar='<video url>',
        help=('TikTok video file URL.'))
    parser.add_argument(
        '-tt', '--tiktok-title', metavar='<title>',
        help=('TikTok video title.'))


def add_instagram_options(parser):
    parser.add_argument(
        '-it', '--instagram-access-token', metavar='<access token>',
        help=('Instagram access token from facebook app.'))
    parser.add_argument(
        '-io', '--instagram-object-id', metavar='<id>',
        help=('Instagram ID of profile where the post is going '
              'to be published.'))
    parser.add_argument(
        '-ip', '--instagram-post-id', metavar='<id>',
        help=('Instagram ID of post to be liked, shared or deleted.'))
    parser.add_argument(
        '-ivu', '--instagram-video-url', metavar='<id>',
        help=('Instagram ID of profile where a post will be shared.'))
    parser.add_argument(
        '-ivt', '--instagram-video-type', metavar='<id>',
        help=('Instagram ID of profile where a post will be shared.'))
    parser.add_argument(
        '-ivc', '--instagram-video-caption', metavar='<id>',
        help=('Instagram ID of profile where a post will be shared.'))


def add_linkedin_options(parser):
    parser.add_argument(
        '-lw', '--linkedin-access-token', metavar='<access token>',
        help=('Your LinkedIn access token.'))
    parser.add_argument(
        '-li', '--linkedin-client-id', metavar='<access token>',
        help=('Your LinkedIn access token.'))
    parser.add_argument(
        '-ls', '--linkedin-client-secret', metavar='<access token>',
        help=('Your LinkedIn access token.'))
    parser.add_argument(
        '-lp', '--linkedin-post-id', metavar='<id>',
        help=('LinkedIn post ID to like, share or delete.'))


def add_common_options(parser):
    parser.add_argument(
        '-l', '--loglevel', default='INFO', metavar='<level>',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help=('Logger verbosity level (default: INFO). Must be one of: '
              'DEBUG, INFO, WARNING, ERROR or CRITICAL.'))
    parser.add_argument(
        '-n', '--network', default='', metavar='<social network>',
        choices=['twitter', 'facebook', 'instagram', 'linkedin',
                 'discord', 'youtube', 'tiktok'],
        help=('Social network to use for publishing (default: ""). '
              'Must be one of: '
              'twitter, facebook, instagram, linkedin, discord, youtube or tiktok.'))
    parser.add_argument(
        '-a', '--action', default='', metavar='<action>',
        choices=['like', 'share', 'last-from-feed', 'random-from-feed',
                 'schedule', 'post', 'video', 'delete', 'authorize'],
        help=('Action to execute (default: ""). '
              'Must be one of: '
              'like, share, last-from-feed, random-from-feed, '
              'schedule, post, video, delete, authorize'))
    parser.add_argument(
        '-st', '--status-text', metavar='<text>',
        help=('Text to be published.'))
    parser.add_argument(
        '-sl', '--status-link', metavar='<link url>',
        help=('Link to be published.'))
    # parser.add_argument(
    #     '-sv', '--status-video', metavar='<video url>',
    #     help=('URL of the video to be published.'))
    parser.add_argument(
        '-i1', '--status-image-url-1', metavar='<image url>',
        help=('First image URL to be published.'))
    parser.add_argument(
        '-i2', '--status-image-url-2', metavar='<image url>',
        help=('Second image URL to be published.'))
    parser.add_argument(
        '-i3', '--status-image-url-3', metavar='<image url>',
        help=('Third image URL to be published.'))
    parser.add_argument(
        '-i4', '--status-image-url-4', metavar='<image url>',
        help=('Fourth image URL to be published.'))
    parser.add_argument(
        '-fu', '--feed-url', metavar='<feed url>',
        help=('URL of public Atom feed to be parsed.'))
    parser.add_argument(
        '-mc', '--feed-max-count', metavar='<number>',
        help=('Max number of new posts to be published at once.'))
    parser.add_argument(
        '-pl', '--feed-post-lookback', metavar='<seconds>',
        help=('Only allow posts published within the last <seconds>.'))
    parser.add_argument(
        '-ma', '--feed-max-post-age', metavar='<days>',
        help=('Dont allow publishing of posts older than this '
              'number of days.'))


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

    add_common_options(publish_options)
    add_twitter_options(publish_options)
    add_facebook_options(publish_options)
    add_instagram_options(publish_options)
    add_linkedin_options(publish_options)
    add_discord_options(publish_options)
    add_youtube_options(publish_options)
    add_tiktok_options(publish_options)
    add_google_sheets_options(publish_options)

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
