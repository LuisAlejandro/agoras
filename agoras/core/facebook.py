import os
import json
import datetime
import random
import time
from urllib.request import urlopen
from html import unescape

import gspread
from pyfacebook import GraphAPI
from atoma import parse_rss_bytes
from google.oauth2.service_account import Credentials


def post(client, facebook_object_id, status_text,
         status_image_url_1=None, status_image_url_2=None,
         status_image_url_3=None, status_image_url_4=None):

    if not facebook_object_id:
        raise Exception('No FACEBOOK_OBJECT_ID provided.')

    attached_media = []
    source_media = filter(None, [
        status_image_url_1, status_image_url_2,
        status_image_url_3, status_image_url_4
    ])

    for imgurl in source_media:

        time.sleep(random.randrange(5))

        imgdata = {'url': imgurl, 'published': False}
        media = client.post_object(object_id=facebook_object_id,
                                   connection='photos',
                                   data=imgdata)
        attached_media.append({'media_fbid': media['id']})

    data = {
        'message': status_text,
        'published': True,
        'attached_media': json.dumps(attached_media)
    }

    time.sleep(random.randrange(5))
    client.post_object(object_id=facebook_object_id,
                       connection='feed',
                       data=data)


def like(client, facebook_object_id, facebook_post_id):
    time.sleep(random.randrange(5))
    client.post_object(object_id=f'{facebook_object_id}_{facebook_post_id}',
                       connection='likes')


def delete(client, facebook_object_id, facebook_post_id):
    time.sleep(random.randrange(5))
    client.delete_object(object_id=f'{facebook_object_id}_{facebook_post_id}')


def share(client, facebook_profile_id, facebook_object_id, facebook_post_id):
    time.sleep(random.randrange(5))
    host = 'https://www.facebook.com'
    data = {
        'link': f'{host}/{facebook_object_id}/posts/{facebook_post_id}'
    }
    client.post_object(object_id=facebook_profile_id,
                       connection='feed',
                       data=data)


def last_from_feed(client, facebook_object_id, feed_url,
                   max_count, post_lookback):

    count = 0

    if not feed_url:
        raise Exception('No FEED_URL provided.')

    if not facebook_object_id:
        raise Exception('No FACEBOOK_PAGE_ID provided.')

    feed_data = parse_rss_bytes(urlopen(feed_url).read())
    today = datetime.datetime.now()
    last_run = today - datetime.timedelta(seconds=post_lookback)
    last_timestamp = int(last_run.strftime('%Y%m%d%H%M%S'))

    for post in feed_data.items:

        if count >= max_count:
            break

        if not post.pub_date or not post.title:
            continue

        item_timestamp = int(post.pub_date.strftime('%Y%m%d%H%M%S'))
        data = {'message': unescape(post.title), 'link': post.guid}

        if item_timestamp > last_timestamp:
            count += 1
            time.sleep(random.randrange(5))
            client.post_object(object_id=facebook_object_id,
                               connection='feed',
                               data=data)


def random_from_feed(client, facebook_object_id, feed_url, max_post_age):

    json_index_content = {}

    if not feed_url:
        raise Exception('No FEED_URL provided.')

    if not facebook_object_id:
        raise Exception('No FACEBOOK_PAGE_ID provided.')

    feed_data = parse_rss_bytes(urlopen(feed_url).read())
    today = datetime.datetime.now()
    max_age_delta = today - datetime.timedelta(days=max_post_age)
    max_age_timestamp = int(max_age_delta.strftime('%Y%m%d%H%M%S'))

    for post in feed_data.items:

        if not post.pub_date:
            continue

        item_timestamp = int(post.pub_date.strftime('%Y%m%d%H%M%S'))

        if int(item_timestamp) >= max_age_timestamp:

            json_index_content[str(item_timestamp)] = {
                'title': post.title,
                'url': post.guid,
                'date': post.pub_date
            }

    random_post_id = random.choice(list(json_index_content.keys()))
    random_post_title = json_index_content[random_post_id]['title']
    status_link = '{0}#{1}'.format(
        json_index_content[random_post_id]['url'],
        today.strftime('%Y%m%d%H%M%S'))
    data = {
        'message': unescape(random_post_title),
        'link': status_link
    }

    time.sleep(random.randrange(5))
    client.post_object(object_id=facebook_object_id,
                       connection='feed',
                       data=data)


def schedule(client, facebook_object_id, google_sheets_id,
             google_sheets_name, google_sheets_client_email,
             google_sheets_private_key):

    newcontent = []
    gspread_scope = ['https://spreadsheets.google.com/feeds']
    account_info = {
        'private_key': google_sheets_private_key,
        'client_email': google_sheets_client_email,
        'token_uri': 'https://oauth2.googleapis.com/token',
    }
    creds = Credentials.from_service_account_info(account_info,
                                                  scopes=gspread_scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(google_sheets_id)

    worksheet = spreadsheet.worksheet(google_sheets_name)
    currdate = datetime.datetime.now()

    content = worksheet.get_all_values()

    for row in content:

        status_text, status_image_url_1, status_image_url_2, \
            status_image_url_3, status_image_url_4, \
            date, hour, state = row

        newcontent.append([
            status_text, status_image_url_1, status_image_url_2,
            status_image_url_3, status_image_url_4,
            date, hour, 'published'
        ])

        if (currdate.strftime('%d-%m-%Y') != date and
           currdate.strftime('%H') != hour) or state == 'published':
            continue

        time.sleep(random.randrange(5))
        post(client, facebook_object_id, status_text,
             status_image_url_1, status_image_url_2,
             status_image_url_3, status_image_url_4)

    worksheet.clear()

    for row in newcontent:
        worksheet.append_row(row)


def main(kwargs):

    action = kwargs.get('action')
    facebook_access_token = kwargs.get(
        'facebook_access_token',
        os.environ.get('FACEBOOK_ACCESS_TOKEN', None))
    facebook_object_id = kwargs.get(
        'facebook_object_id',
        os.environ.get('FACEBOOK_OBJECT_ID', None))
    facebook_post_id = kwargs.get('facebook_post_id', None) or \
        os.environ.get('FACEBOOK_POST_ID', None)
    facebook_profile_id = kwargs.get(
        'facebook_profile_id',
        os.environ.get('FACEBOOK_PROFILE_ID', None))
    status_text = kwargs.get('status_text', None) or \
        os.environ.get('STATUS_TEXT', None)
    status_image_url_1 = kwargs.get('status_image_url_1', None) or \
        os.environ.get('STATUS_IMAGE_URL_1', None)
    status_image_url_2 = kwargs.get('status_image_url_2', None) or \
        os.environ.get('STATUS_IMAGE_URL_2', None)
    status_image_url_3 = kwargs.get('status_image_url_3', None) or \
        os.environ.get('STATUS_IMAGE_URL_3', None)
    status_image_url_4 = kwargs.get('status_image_url_4', None) or \
        os.environ.get('STATUS_IMAGE_URL_4', None)
    feed_url = kwargs.get('feed_url', None) or \
        os.environ.get('FEED_URL', None)
    post_lookback = kwargs.get('post_lookback', 1 * 60 * 60) or \
        os.environ.get('POST_LOOKBACK', 1 * 60 * 60)
    max_count = kwargs.get('max_count', 1) or \
        os.environ.get('MAX_COUNT', 1)
    max_post_age = kwargs.get('max_post_age', 365) or \
        os.environ.get('MAX_POST_AGE', 365)
    google_sheets_id = kwargs.get('google_sheets_id', None) or \
        os.environ.get('GOOGLE_SHEETS_ID', None)
    google_sheets_name = kwargs.get('google_sheets_name', None) or \
        os.environ.get('GOOGLE_SHEETS_NAME', None)
    google_sheets_client_email = \
        kwargs.get('google_sheets_client_email', None) or \
        os.environ.get('GOOGLE_SHEETS_CLIENT_EMAIL', None)
    google_sheets_private_key = \
        kwargs.get('google_sheets_private_key', None) or \
        os.environ.get('GOOGLE_SHEETS_PRIVATE_KEY', None)

    max_count = int(max_count)
    post_lookback = int(post_lookback)
    max_post_age = int(max_post_age)
    google_sheets_private_key = \
        google_sheets_private_key.replace('\\n', '\n') \
        if google_sheets_private_key else ''

    client = GraphAPI(access_token=facebook_access_token, version="13.0")

    if action == 'post':
        post(client, facebook_object_id, status_text,
             status_image_url_1, status_image_url_2,
             status_image_url_3, status_image_url_4)
    elif action == 'like':
        like(client, facebook_object_id, facebook_post_id)
    elif action == 'delete':
        delete(client, facebook_object_id, facebook_post_id)
    elif action == 'share':
        share(client, facebook_profile_id, facebook_object_id,
              facebook_post_id)
    elif action == 'last-from-feed':
        last_from_feed(client, facebook_object_id, feed_url,
                       max_count, post_lookback)
    elif action == 'random-from-feed':
        random_from_feed(client, facebook_object_id, feed_url, max_post_age)
    elif action == 'schedule':
        schedule(client, facebook_object_id, google_sheets_id,
                 google_sheets_name, google_sheets_client_email,
                 google_sheets_private_key)
    elif action == '':
        raise Exception('--action is a required argument.')
    else:
        raise Exception(f'"{action}" action not supported.')
