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

import datetime
import json
import os
import random
import tempfile
import time
from html import unescape
from urllib.request import Request, urlopen

import filetype
import gspread
from atoma import parse_rss_bytes
from dateutil import parser
from google.oauth2.service_account import Credentials
from pyfacebook import GraphAPI

from agoras import __version__
from agoras.core.utils import add_url_timestamp


def post(client, facebook_object_id, status_text, status_link,
         status_image_url_1=None, status_image_url_2=None,
         status_image_url_3=None, status_image_url_4=None):

    if not facebook_object_id:
        raise Exception('No --facebook-object-id provided.')

    attached_media = []
    source_media = list(filter(None, [
        status_image_url_1, status_image_url_2,
        status_image_url_3, status_image_url_4
    ]))

    if not source_media and not status_text and not status_link:
        raise Exception('No --status-text or --status-link or --status-image-url-1 provided.')

    for imgurl in source_media:

        _, tmpimg = tempfile.mkstemp(prefix='status-image-url-',
                                     suffix='.bin')

        with open(tmpimg, 'wb') as i:
            request = Request(url=imgurl, headers={'User-Agent': f'Agoras/{__version__}'})
            i.write(urlopen(request).read())

        kind = filetype.guess(tmpimg)

        if not kind:
            raise Exception(f'Invalid image type for {imgurl}')

        if kind.mime not in ['image/jpeg', 'image/png', 'image/gif']:
            raise Exception(f'Invalid image type: {kind.mime}')

        time.sleep(random.randrange(5))
        media = client.post_object(object_id=facebook_object_id,
                                   connection='photos',
                                   data={
                                       'url': imgurl,
                                       'published': False
                                   })
        attached_media.append({
            'media_fbid': media['id']
        })

    data = {
        'published': True,
    }

    if status_link:
        data['link'] = status_link

    if status_text:
        data['message'] = status_text

    if attached_media:
        data['attached_media'] = json.dumps(attached_media)  # type: ignore

    time.sleep(random.randrange(5))
    request = client.post_object(object_id=facebook_object_id,
                                 connection='feed',
                                 data=data)
    status = {
        "id": request['id'].split('_')[1]
    }
    print(json.dumps(status, separators=(',', ':')))


def like(client, facebook_object_id, facebook_post_id):
    time.sleep(random.randrange(5))
    client.post_object(
        object_id=f'{facebook_object_id}_{facebook_post_id}',
        connection='likes')
    status = {
        "id": facebook_post_id
    }
    print(json.dumps(status, separators=(',', ':')))


def delete(client, facebook_object_id, facebook_post_id):
    time.sleep(random.randrange(5))
    client.delete_object(object_id=f'{facebook_object_id}_{facebook_post_id}')
    status = {
        "id": facebook_post_id
    }
    print(json.dumps(status, separators=(',', ':')))


def share(client, facebook_profile_id, facebook_object_id, facebook_post_id):
    time.sleep(random.randrange(5))
    host = 'https://www.facebook.com'
    data = {
        'link': f'{host}/{facebook_object_id}/posts/{facebook_post_id}',
        'published': True
    }
    request = client.post_object(object_id=facebook_profile_id,
                                 connection='feed',
                                 data=data)
    status = {
        "id": request['id'].split('_')[1]
    }
    print(json.dumps(status, separators=(',', ':')))


def last_from_feed(client, facebook_object_id, feed_url,
                   max_count, post_lookback):

    count = 0

    if not feed_url:
        raise Exception('No --feed-url provided.')

    if not facebook_object_id:
        raise Exception('No --facebook-object-id provided.')

    request = Request(url=feed_url, headers={'User-Agent': f'Agoras/{__version__}'})
    feed_data = parse_rss_bytes(urlopen(request).read())
    today = datetime.datetime.now()
    last_run = today - datetime.timedelta(seconds=post_lookback)
    last_timestamp = int(last_run.strftime('%Y%m%d%H%M%S'))

    for item in feed_data.items:

        if count >= max_count:
            break

        if not item.pub_date:
            continue

        item_timestamp = int(item.pub_date.strftime('%Y%m%d%H%M%S'))

        if item_timestamp < last_timestamp:
            continue

        link = item.link or item.guid or ''
        title = item.title or ''

        status_link = add_url_timestamp(link, today.strftime('%Y%m%d%H%M%S')) if link else ''
        status_title = unescape(title) if title else ''

        try:
            status_image = item.enclosures[0].url
        except Exception:
            status_image = ''

        count += 1
        post(client, facebook_object_id, status_title, status_link, status_image)


def random_from_feed(client, facebook_object_id, feed_url, max_post_age):

    json_index_content = {}

    if not feed_url:
        raise Exception('No --feed-url provided.')

    if not facebook_object_id:
        raise Exception('No --facebook-object-id provided.')

    request = Request(url=feed_url, headers={'User-Agent': f'Agoras/{__version__}'})
    feed_data = parse_rss_bytes(urlopen(request).read())
    today = datetime.datetime.now()
    max_age_delta = today - datetime.timedelta(days=max_post_age)
    max_age_timestamp = int(max_age_delta.strftime('%Y%m%d%H%M%S'))

    for item in feed_data.items:

        if not item.pub_date:
            continue

        item_timestamp = int(item.pub_date.strftime('%Y%m%d%H%M%S'))

        if item_timestamp < max_age_timestamp:
            continue

        json_index_content[str(item_timestamp)] = {
            'title': item.title or '',
            'url': item.link or item.guid or '',
            'date': item.pub_date
        }

        try:
            json_index_content[str(item_timestamp)]['image'] = item.enclosures[0].url
        except Exception:
            json_index_content[str(item_timestamp)]['image'] = ''

    random_status_id = random.choice(list(json_index_content.keys()))
    random_status_title = json_index_content[random_status_id]['title']
    random_status_image = json_index_content[random_status_id]['image']
    random_status_link = json_index_content[random_status_id]['url']

    status_link = add_url_timestamp(random_status_link, today.strftime('%Y%m%d%H%M%S')) if random_status_link else ''
    status_title = unescape(random_status_title) if random_status_title else ''

    post(client, facebook_object_id, status_title, status_link, random_status_image)


def schedule(client, facebook_object_id, google_sheets_id,
             google_sheets_name, google_sheets_client_email,
             google_sheets_private_key, max_count):

    count = 0
    newcontent = []
    gspread_scope = ['https://spreadsheets.google.com/feeds']
    account_info = {
        'private_key': google_sheets_private_key,
        'client_email': google_sheets_client_email,
        'token_uri': 'https://oauth2.googleapis.com/token',
    }
    creds = Credentials.from_service_account_info(account_info,
                                                  scopes=gspread_scope)
    gclient = gspread.authorize(creds)
    spreadsheet = gclient.open_by_key(google_sheets_id)

    worksheet = spreadsheet.worksheet(google_sheets_name)
    currdate = datetime.datetime.now()

    content = worksheet.get_all_values()

    for row in content:

        status_text, status_link, status_image_url_1, status_image_url_2, \
            status_image_url_3, status_image_url_4, \
            date, hour, state = row

        newcontent.append([
            status_text, status_link, status_image_url_1, status_image_url_2,
            status_image_url_3, status_image_url_4,
            date, hour, state
        ])

        rowdate = parser.parse(date)
        normalized_currdate = parser.parse(currdate.strftime('%d-%m-%Y'))
        normalized_rowdate = parser.parse(rowdate.strftime('%d-%m-%Y'))

        if count >= max_count:
            break

        if state == 'published':
            continue

        if normalized_rowdate < normalized_currdate:
            continue

        if currdate.strftime('%d-%m-%Y') == rowdate.strftime('%d-%m-%Y') and \
           currdate.strftime('%H') != hour:
            continue

        count += 1
        newcontent[-1][-1] = 'published'
        post(client, facebook_object_id, status_text, status_link,
             status_image_url_1, status_image_url_2,
             status_image_url_3, status_image_url_4)

    worksheet.clear()

    for row in newcontent:
        worksheet.append_row(row, table_range='A1')


def main(kwargs):

    action = kwargs.get('action')
    facebook_access_token = kwargs.get('facebook_access_token', None) or \
        os.environ.get('FACEBOOK_ACCESS_TOKEN', None)
    facebook_object_id = kwargs.get('facebook_object_id', None) or \
        os.environ.get('FACEBOOK_OBJECT_ID', None)
    facebook_post_id = kwargs.get('facebook_post_id', None) or \
        os.environ.get('FACEBOOK_POST_ID', None)
    facebook_profile_id = kwargs.get('facebook_profile_id', None) or \
        os.environ.get('FACEBOOK_PROFILE_ID', None)
    status_text = kwargs.get('status_text', '') or \
        os.environ.get('STATUS_TEXT', '')
    status_link = kwargs.get('status_link', '') or \
        os.environ.get('STATUS_LINK', '')
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

    client = GraphAPI(access_token=facebook_access_token, version="14.0")

    if action == 'post':
        post(client, facebook_object_id, status_text, status_link,
             status_image_url_1, status_image_url_2,
             status_image_url_3, status_image_url_4)
    elif action == 'like':
        like(client, facebook_object_id, facebook_post_id)
    elif action == 'share':
        share(client, facebook_profile_id, facebook_object_id,
              facebook_post_id)
    elif action == 'delete':
        delete(client, facebook_object_id, facebook_post_id)
    elif action == 'last-from-feed':
        last_from_feed(client, facebook_object_id, feed_url,
                       max_count, post_lookback)
    elif action == 'random-from-feed':
        random_from_feed(client, facebook_object_id, feed_url, max_post_age)
    elif action == 'schedule':
        schedule(client, facebook_object_id, google_sheets_id,
                 google_sheets_name, google_sheets_client_email,
                 google_sheets_private_key, max_count)
    elif action == '':
        raise Exception('--action is a required argument.')
    else:
        raise Exception(f'"{action}" action not supported.')
