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
from linkedin_api.clients.restli.client import RestliClient
import requests

from agoras import __version__
from agoras.core.utils import add_url_timestamp, parse_metatags


api_version = "202302"


def get_object_id(client, linkedin_access_token):
    me = client.get(resource_path='/userinfo', access_token=linkedin_access_token)
    linkedin_object_id = me.response.json().get('sub', '')
    if not linkedin_object_id:
        raise Exception('Unable to get LinkedIn object ID.')
    return linkedin_object_id


def get_entity(
        linkedin_object_id,
        status_text,
        status_link,
        status_link_title,
        status_link_description,
        attached_media):

    entity = {
        "author": f"urn:li:person:{linkedin_object_id}",
        "commentary": status_text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False
    }

    if status_link and status_text:
        entity["content"] = {
            "article": {
                "source": status_link,
                "title": status_text,
            }
        }

        if len(attached_media) > 0:
            entity["content"]["article"]["thumbnail"] = attached_media[0]['id']

        if status_link_title:
            entity["content"]["article"]["title"] = status_link_title

        if status_link_description:
            entity["content"]["article"]["description"] = status_link_description

    if not status_link:
        if len(attached_media) == 1:
            entity["content"] = {
                "media": attached_media[0]
            }

        elif len(attached_media) > 1:
            entity["content"] = {
                "multiImage": {
                    "images": attached_media
                }
            }

    return entity


def post(client, linkedin_access_token, status_text, status_link,
         status_image_url_1=None, status_image_url_2=None,
         status_image_url_3=None, status_image_url_4=None):

    if not linkedin_access_token:
        raise Exception('No --linkedin-access-token provided.')

    status_link_title = ''
    status_link_description = ''
    status_link_image = ''
    attached_media = []
    source_media = list(filter(None, [
        status_image_url_1, status_image_url_2,
        status_image_url_3, status_image_url_4
    ]))

    if not source_media and not status_text and not status_link:
        raise Exception('No --status-text or --status-link or --status-image-url-1 provided.')

    linkedin_object_id = get_object_id(client, linkedin_access_token)

    if status_link:
        scraped_data = parse_metatags(status_link)
        status_link_title = scraped_data.get('title', '')
        status_link_description = scraped_data.get('description', '')
        status_link_image = scraped_data.get('image', '')

        if status_link_image:
            source_media = [status_link_image]

    for imgurl in source_media:

        _, tmpimg = tempfile.mkstemp(prefix='status-image-url-',
                                     suffix='.bin')

        with open(tmpimg, 'wb') as i:
            request = Request(url=imgurl, headers={'User-Agent': f'Agoras/{__version__}'})
            imgcontent = urlopen(request).read()
            i.write(imgcontent)

        kind = filetype.guess(tmpimg)

        if not kind:
            raise Exception(f'Invalid image type for {imgurl}')

        if kind.mime not in ['image/jpeg', 'image/png', 'image/gif']:
            raise Exception(f'Invalid image type "{kind.mime}" for {imgurl}')

        request = client.action(
            resource_path="/images",
            action_name="initializeUpload",
            action_params={
                "initializeUploadRequest": {
                    "owner": f"urn:li:person:{linkedin_object_id}",
                }
            },
            version_string=api_version,
            access_token=linkedin_access_token
        )

        response = request.response.json()
        upload_url = response.get('value', {}).get('uploadUrl', '')
        media_id = response.get('value', {}).get('image', '')

        time.sleep(random.randrange(5))

        try:
            response = requests.put(
                upload_url,
                headers={
                    'Authorization': f'Bearer {linkedin_access_token}'},
                data=imgcontent)
        except Exception:
            continue

        if response.status_code != 201:
            continue

        attached_media.append({
            "id": media_id,
        })

    entity = get_entity(
        linkedin_object_id,
        status_text,
        status_link,
        status_link_title,
        status_link_description,
        attached_media)

    time.sleep(random.randrange(5))

    request = client.create(
        resource_path='/posts',
        entity=entity,
        version_string=api_version,
        access_token=linkedin_access_token
    )

    status = {
        'id': request.entity_id
    }
    print(json.dumps(status, separators=(',', ':')))


def like(client, linkedin_access_token, linkedin_post_id):
    linkedin_object_id = get_object_id(client, linkedin_access_token)

    time.sleep(random.randrange(5))

    entity = {
        "actor": f"urn:li:person:{linkedin_object_id}",
        "object": linkedin_post_id,
    }

    request = client.create(
        resource_path='/socialActions/{id}/likes',
        path_keys={
            "id": linkedin_post_id,
        },
        entity=entity,
        version_string=api_version,
        access_token=linkedin_access_token
    )

    if request.status_code != 201:
        raise Exception(f'Unable to like post {linkedin_post_id}')

    status = {
        'id': linkedin_post_id,
    }
    print(json.dumps(status, separators=(',', ':')))


def share(client, linkedin_access_token, linkedin_post_id):
    linkedin_object_id = get_object_id(client, linkedin_access_token)

    time.sleep(random.randrange(5))

    entity = {
        "author": f"urn:li:person:{linkedin_object_id}",
        "commentary": "",
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": []
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
        "reshareContext": {
            "parent": linkedin_post_id
        }
    }

    request = client.create(
        resource_path='/posts',
        entity=entity,
        version_string=api_version,
        access_token=linkedin_access_token
    )

    if request.status_code != 201:
        raise Exception(f'Unable to share post {linkedin_post_id}')

    status = {
        'id': request.entity_id
    }
    print(json.dumps(status, separators=(',', ':')))


def delete(client, linkedin_access_token, linkedin_post_id):
    time.sleep(random.randrange(5))

    request = client.delete(
        resource_path='/posts/{id}',
        path_keys={
            "id": linkedin_post_id,
        },
        version_string=api_version,
        access_token=linkedin_access_token
    )

    if request.status_code != 204:
        raise Exception(f'Unable to delete post {linkedin_post_id}')

    status = {
        'id': linkedin_post_id
    }
    print(json.dumps(status, separators=(',', ':')))


def last_from_feed(client, linkedin_access_token, feed_url, max_count, post_lookback):

    count = 0

    if not feed_url:
        raise Exception('No --feed-url provided.')

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
        post(client, linkedin_access_token, status_title, status_link, status_image)


def random_from_feed(client, linkedin_access_token, feed_url, max_post_age):

    json_index_content = {}

    if not feed_url:
        raise Exception('No --feed-url provided.')

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

    post(client, linkedin_access_token, status_title, status_link, random_status_image)


def schedule(client, linkedin_access_token, google_sheets_id,
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
        post(client, linkedin_access_token, status_text, status_link,
             status_image_url_1, status_image_url_2,
             status_image_url_3, status_image_url_4)

    worksheet.clear()

    for row in newcontent:
        worksheet.append_row(row, table_range='A1')


def main(kwargs):

    action = kwargs.get('action')
    linkedin_access_token = kwargs.get('linkedin_access_token', None) or \
        os.environ.get('LINKEDIN_ACCESS_TOKEN', None)
    linkedin_post_id = kwargs.get('linkedin_post_id', None) or \
        os.environ.get('LINKEDIN_POST_ID', None)
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

    client = RestliClient()

    if action == 'post':
        post(client, linkedin_access_token, status_text, status_link,
             status_image_url_1, status_image_url_2,
             status_image_url_3, status_image_url_4)
    elif action == 'like':
        like(client, linkedin_access_token, linkedin_post_id)
    elif action == 'share':
        share(client, linkedin_access_token, linkedin_post_id)
    elif action == 'delete':
        delete(client, linkedin_access_token, linkedin_post_id)
    elif action == 'last-from-feed':
        last_from_feed(client, linkedin_access_token, feed_url,
                       max_count, post_lookback)
    elif action == 'random-from-feed':
        random_from_feed(client, linkedin_access_token, feed_url, max_post_age)
    elif action == 'schedule':
        schedule(client, linkedin_access_token, google_sheets_id,
                 google_sheets_name, google_sheets_client_email,
                 google_sheets_private_key, max_count)
    elif action == '':
        raise Exception('--action is a required argument.')
    else:
        raise Exception(f'"{action}" action not supported.')
