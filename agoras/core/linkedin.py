# -*- coding: utf-8 -*-
#
# Please refer to AUTHORS.md for a complete list of Copyright holders.
# Copyright (C) 2016-2022, Agoras Developers.

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
import json
import datetime
import random
import tempfile
import time
from urllib.request import urlopen
from urllib.parse import quote
from html import unescape

import gspread
from linkedin_api import Linkedin
from atoma import parse_rss_bytes
from google.oauth2.service_account import Credentials


api_url_host = 'https://www.linkedin.com/voyager'
media_upload_endpoint = (
    f'{api_url_host}'
    '/api/voyagerVideoDashMediaUploadMetadata?action=upload')
content_creation_endpoint = (
    f'{api_url_host}/api/contentcreation/normShares')
social_reactions_endpoint = (
    f'{api_url_host}/api/voyagerSocialDashReactions')
updates_endpoint = (
    f'{api_url_host}/api/feed/updatesV2?commentsCount=0'
    '&likesCount=0&q=backendUrnOrNss')


def post(client, status_text,
         status_image_url_1=None, status_image_url_2=None,
         status_image_url_3=None, status_image_url_4=None):

    attached_media = []
    source_media = filter(None, [
        status_image_url_1, status_image_url_2,
        status_image_url_3, status_image_url_4
    ])

    for imgurl in source_media:

        _, tmpimg = tempfile.mkstemp(prefix='status-image-url-',
                                     suffix='.bin')

        with open(tmpimg, 'wb') as i:
            i.write(urlopen(imgurl).read())

        media = client.client.session.post(
            media_upload_endpoint,
            json.dumps({
                'mediaUploadType': 'IMAGE_SHARING',
                'fileSize': os.stat(tmpimg).st_size,
                'filename': tmpimg
            })
        )

        media_response = media.json()
        media_upload_url = media_response['value']['singleUploadUrl']
        media_urn = media_response['value']['urn']

        time.sleep(random.randrange(5))

        with open(tmpimg, 'rb') as i:
            client.client.session.put(media_upload_url, i)

        attached_media.append({
            'category': 'IMAGE',
            'mediaUrn': media_urn,
            'tapTargets': []
        })

    time.sleep(random.randrange(5))

    status = client.client.session.post(
        content_creation_endpoint,
        json.dumps({
            'visibleToConnectionsOnly': False,
            'commentsDisabled': False,
            'externalAudienceProviders': [],
            'commentaryV2': {
                'text': status_text,
                'attributes': []
            },
            'origin': 'FEED',
            'allowedCommentersScope': 'ALL',
            'media': attached_media
        })
    )
    print(status.json())


def like(client, linkedin_post_id):
    time.sleep(random.randrange(5))
    media_urn = quote(f'urn:li:activity:{linkedin_post_id}')
    client.client.session.post(
        f'{social_reactions_endpoint}?threadUrn={media_urn}',
        json.dumps({'reactionType': 'LIKE'})
    )
    print(linkedin_post_id)


def share(client, linkedin_post_id):
    time.sleep(random.randrange(5))
    media_urn = quote(f'urn:li:activity:{linkedin_post_id}')
    metadata = client.client.session.get(
        f'{updates_endpoint}&urnOrNss={media_urn}'
    )
    metadata_response = metadata.json()
    share_urn = metadata_response['elements'][0]['updateMetadata']['shareUrn']
    status = client.client.session.post(
        content_creation_endpoint,
        json.dumps({
            "visibleToConnectionsOnly": False,
            "externalAudienceProviders": [],
            "commentaryV2": {
                "text": "",
                "attributes": []
            },
            "origin": "SHARE_AS_IS",
            "allowedCommentersScope": "NONE",
            "postState": "PUBLISHED",
            "parentUrn": share_urn})
    )
    print(status.json())


def delete(client, linkedin_post_id):
    time.sleep(random.randrange(5))
    media_urn = quote(f'urn:li:activity:{linkedin_post_id}')
    metadata = client.client.session.get(
        f'{updates_endpoint}&urnOrNss={media_urn}'
    )
    metadata_response = metadata.json()
    share_urn = metadata_response['elements'][0]['updateMetadata']['shareUrn']
    client.client.session.delete(
        f'{content_creation_endpoint}/{share_urn}'
    )
    print(linkedin_post_id)


def last_from_feed(client, feed_url, max_count, post_lookback):

    count = 0

    if not feed_url:
        raise Exception('No FEED_URL provided.')

    feed_data = parse_rss_bytes(urlopen(feed_url).read())
    today = datetime.datetime.now()
    last_run = today - datetime.timedelta(seconds=post_lookback)
    last_timestamp = int(last_run.strftime('%Y%m%d%H%M%S'))

    for item in feed_data.items:

        if count >= max_count:
            break

        if not item.pub_date or not item.title:
            continue

        item_timestamp = int(item.pub_date.strftime('%Y%m%d%H%M%S'))

        if item_timestamp > last_timestamp:
            count += 1
            post(client, unescape(item.title), item.guid)


def random_from_feed(client, feed_url, max_post_age):

    json_index_content = {}

    if not feed_url:
        raise Exception('No FEED_URL provided.')

    feed_data = parse_rss_bytes(urlopen(feed_url).read())
    today = datetime.datetime.now()
    max_age_delta = today - datetime.timedelta(days=max_post_age)
    max_age_timestamp = int(max_age_delta.strftime('%Y%m%d%H%M%S'))

    for item in feed_data.items:

        if not item.pub_date:
            continue

        item_timestamp = int(item.pub_date.strftime('%Y%m%d%H%M%S'))

        if int(item_timestamp) >= max_age_timestamp:

            json_index_content[str(item_timestamp)] = {
                'title': item.title,
                'url': item.guid,
                'date': item.pub_date
            }

    random_post_id = random.choice(list(json_index_content.keys()))
    random_post_title = json_index_content[random_post_id]['title']
    status_link = '{0}#{1}'.format(
        json_index_content[random_post_id]['url'],
        today.strftime('%Y%m%d%H%M%S'))
    post(client, unescape(random_post_title), status_link)


def schedule(client, google_sheets_id,
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

        post(client, status_text,
             status_image_url_1, status_image_url_2,
             status_image_url_3, status_image_url_4)

    worksheet.clear()

    for row in newcontent:
        worksheet.append_row(row)


def main(kwargs):

    action = kwargs.get('action')
    linkedin_username = kwargs.get(
        'linkedin_username',
        os.environ.get('LINKEDIN_USERNAME', None))
    linkedin_password = kwargs.get(
        'linkedin_password',
        os.environ.get('LINKEDIN_PASSWORD', None))
    linkedin_post_id = kwargs.get('linkedin_post_id', None) or \
        os.environ.get('LINKEDIN_POST_ID', None)
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

    client = Linkedin(linkedin_username, linkedin_password)

    if action == 'post':
        post(client, status_text,
             status_image_url_1, status_image_url_2,
             status_image_url_3, status_image_url_4)
    elif action == 'like':
        like(client, linkedin_post_id)
    elif action == 'share':
        share(client, linkedin_post_id)
    elif action == 'delete':
        delete(client, linkedin_post_id)
    elif action == 'last-from-feed':
        last_from_feed(client, feed_url,
                       max_count, post_lookback)
    elif action == 'random-from-feed':
        random_from_feed(client, feed_url, max_post_age)
    elif action == 'schedule':
        schedule(client, google_sheets_id,
                 google_sheets_name, google_sheets_client_email,
                 google_sheets_private_key)
    elif action == '':
        raise Exception('--action is a required argument.')
    else:
        raise Exception(f'"{action}" action not supported.')
