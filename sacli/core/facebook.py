import os
import json
import datetime
from urllib.request import urlopen
from html import unescape
from random import choice

from pyfacebook import GraphAPI
from atoma import parse_rss_bytes


def post(client, page_id, status_text,
         status_image_url_1, status_image_url_2,
         status_image_url_3, status_image_url_4):

    if not page_id:
        raise Exception('No FACEBOOK_PAGE_ID provided.')

    attached_media = []

    for imgurl in [status_image_url_1,
                   status_image_url_2,
                   status_image_url_3,
                   status_image_url_4]:

        if not imgurl:
            continue

        imgdata = {'url': imgurl, 'published': False}
        media = client.post_object(object_id=page_id,
                                   connection='photos',
                                   data=imgdata)
        attached_media.append({'media_fbid': media['id']})

    data = {
        'message': status_text,
        'published': True,
        'attached_media': json.dumps(attached_media)
    }

    client.post_object(object_id=page_id,
                       connection='feed',
                       data=data)


def like(kwargs):
    pass


def share(kwargs):
    pass


def last_from_feed(client, page_id, feed_url, max_count, post_lookback):

    count = 0

    if not feed_url:
        raise Exception('No FEED_URL provided.')

    if not page_id:
        raise Exception('No FACEBOOK_PAGE_ID provided.')

    feed_data = parse_rss_bytes(urlopen(feed_url).read())
    today = datetime.datetime.now()
    last_run = today - datetime.timedelta(seconds=post_lookback)
    last_timestamp = int(last_run.strftime('%Y%m%d%H%M%S'))

    for post in feed_data.items:

        if count >= max_count:
            break

        item_timestamp = int(post.pub_date.strftime('%Y%m%d%H%M%S'))
        data = {'message': unescape(post.title), 'link': post.guid}

        if item_timestamp > last_timestamp:
            count += 1
            client.post_object(object_id=page_id,
                               connection='feed',
                               data=data)


def random_from_feed(client, page_id, feed_url, max_post_age):

    json_index_content = {}

    if not feed_url:
        raise Exception('No FEED_URL provided.')

    if not page_id:
        raise Exception('No FACEBOOK_PAGE_ID provided.')

    feed_data = parse_rss_bytes(urlopen(feed_url).read())
    today = datetime.datetime.now()
    max_age_delta = today - datetime.timedelta(days=max_post_age)
    max_age_timestamp = int(max_age_delta.strftime('%Y%m%d%H%M%S'))

    for post in feed_data.items:

        item_timestamp = post.pub_date.strftime('%Y%m%d%H%M%S')

        if int(item_timestamp) >= max_age_timestamp:
            json_index_content[item_timestamp] = {
                'title': post.title,
                'url': post.guid,
                'date': post.pub_date
            }

    random_post_id = choice(list(json_index_content.keys()))
    random_post_title = json_index_content[random_post_id]['title']
    status_link = '{0}#{1}'.format(
        json_index_content[random_post_id]['url'],
        today.strftime('%Y%m%d%H%M%S'))
    data = {'message': unescape(random_post_title), 'link': status_link}

    client.post_object(object_id=page_id,
                       connection='feed',
                       data=data)


def schedule(kwargs):
    pass


def main(kwargs):

    action = kwargs.get('action')
    access_token = kwargs.get(
        'access_token', os.environ.get('FACEBOOK_ACCESS_TOKEN', None))
    page_id = kwargs.get(
        'page_id', os.environ.get('FACEBOOK_PAGE_ID', None))
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

    client = GraphAPI(access_token=access_token, version="13.0")

    if action == 'post':
        post(client, page_id, status_text,
             status_image_url_1, status_image_url_2,
             status_image_url_3, status_image_url_4)
    elif action == 'like':
        like(kwargs)
    elif action == 'share':
        share(kwargs)
    elif action == 'last-from-feed':
        last_from_feed(client, page_id, feed_url, max_count, post_lookback)
    elif action == 'random-from-feed':
        random_from_feed(client, page_id, feed_url, max_post_age)
    elif action == 'schedule':
        schedule(kwargs)
    elif action == '':
        raise Exception('--action is a required argument.')

    raise Exception(f'"{action}" action not supported.')
