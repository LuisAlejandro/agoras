# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
# Copyright (C) 2020-2022 Luis Alejandro Martínez Faneyth.

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

import os
import datetime
import tempfile
from urllib.request import urlopen
from html import unescape
from random import choice

from atoma import parse_rss_bytes
from tweepy import OAuth1UserHandler, API


def post(client, status_text,
         status_image_url_1, status_image_url_2,
         status_image_url_3, status_image_url_4):

    media_ids = []

    for imgurl in [status_image_url_1,
                   status_image_url_2,
                   status_image_url_3,
                   status_image_url_4]:

        if not imgurl:
            continue

        _, tmpimg = tempfile.mkstemp(prefix='status-image-url-', suffix='.bin')

        with open(tmpimg, 'wb') as i:
            i.write(urlopen(imgurl).read())

        media = client.media_upload(tmpimg)
        media_ids.append(media.media_id)

    client.update_status(status_text, media_ids=media_ids)


def like(kwargs):
    pass


def share(kwargs):
    pass


def last_from_feed(client, feed_url, max_count, post_lookback):

    count = 0

    if not feed_url:
        raise Exception('No FEED_URL provided.')

    feed_data = parse_rss_bytes(urlopen(feed_url).read())
    today = datetime.datetime.now()
    last_run = today - datetime.timedelta(seconds=post_lookback)
    last_timestamp = int(last_run.strftime('%Y%m%d%H%M%S'))

    for post in feed_data.items:

        if count >= max_count:
            break

        item_timestamp = int(post.pub_date.strftime('%Y%m%d%H%M%S'))
        status_text = '{0} {1}'.format(unescape(post.title), post.guid)

        if item_timestamp > last_timestamp:
            count += 1
            client.update_status(status_text)


def random_from_feed(client, feed_url, max_post_age):

    json_index_content = {}

    if not feed_url:
        raise Exception('No FEED_URL provided.')

    feed_data = parse_rss_bytes(urlopen(feed_url).read())
    today = datetime.datetime.now()
    max_age_delta = today - datetime.timedelta(days=max_post_age)
    max_age_timestamp = int(max_age_delta.strftime('%Y%m%d%H%M%S'))

    for post in feed_data.items:

        item_timestamp = int(post.pub_date.strftime('%Y%m%d%H%M%S'))

        if item_timestamp > max_age_timestamp:

            json_index_content[str(item_timestamp)] = {
                'title': post.title,
                'url': post.guid,
                'date': post.pub_date
            }

    random_post_id = choice(list(json_index_content.keys()))
    random_post_title = json_index_content[random_post_id]['title']
    status_text = '{0} {1}#{2}'.format(
        unescape(random_post_title),
        json_index_content[random_post_id]['url'],
        today.strftime('%Y%m%d%H%M%S'))

    client.update_status(status_text)


def schedule(kwargs):
    pass


def main(kwargs):

    action = kwargs.get('action')
    consumer_key = kwargs.get(
        'consumer_key', os.environ.get('TWITTER_CONSUMER_KEY', None))
    consumer_secret = kwargs.get(
        'consumer_secret', os.environ.get('TWITTER_CONSUMER_SECRET', None))
    oauth_token = kwargs.get(
        'oauth_token', os.environ.get('TWITTER_OAUTH_TOKEN', None))
    oauth_secret = kwargs.get(
        'oauth_secret', os.environ.get('TWITTER_OAUTH_SECRET', None))
    status_text = kwargs.get(
        'status_text', os.environ.get('STATUS_TEXT', None))
    status_image_url_1 = kwargs.get(
        'status_image_url_1', os.environ.get('STATUS_IMAGE_URL_1', None))
    status_image_url_2 = kwargs.get(
        'status_image_url_2', os.environ.get('STATUS_IMAGE_URL_2', None))
    status_image_url_3 = kwargs.get(
        'status_image_url_3', os.environ.get('STATUS_IMAGE_URL_3', None))
    status_image_url_4 = kwargs.get(
        'status_image_url_4', os.environ.get('STATUS_IMAGE_URL_4', None))
    feed_url = kwargs.get(
        'feed_url', os.environ.get('FEED_URL', None))
    post_lookback = int(kwargs.get(
        'post_lookback', os.environ.get('POST_LOOKBACK', 1 * 60 * 60)))
    max_count = int(kwargs.get(
        'max_count', os.environ.get('MAX_COUNT', 1)))
    max_post_age = int(kwargs.get(
        'max_post_age', os.environ.get('MAX_POST_AGE', 365)))

    auth = OAuth1UserHandler(consumer_key, consumer_secret,
                             oauth_token, oauth_secret)
    client = API(auth, wait_on_rate_limit=True)

    if action == 'like':
        like(kwargs)
    elif action == 'share':
        share(kwargs)
    elif action == 'last-from-feed':
        last_from_feed(client, feed_url, max_count, post_lookback)
    elif action == 'random-from-feed':
        random_from_feed(client, feed_url, max_post_age)
    elif action == 'schedule':
        schedule(kwargs)
    elif action == 'post':
        post(client, status_text,
             status_image_url_1, status_image_url_2,
             status_image_url_3, status_image_url_4)
    elif action == '':
        raise Exception('--action is a required argument.')

    raise Exception(f'"{action}" action not supported.')
