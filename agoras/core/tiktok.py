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
from html import unescape
from urllib.request import Request, urlopen

import filetype
import requests
import gspread
from atoma import parse_rss_bytes
from dateutil import parser
from google.oauth2.service_account import Credentials

from agoras import __version__


CREATOR_INFO_URL = "https://open.tiktokapis.com/v2/post/publish/creator_info/query/"
DIRECT_POST_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"
GET_VIDEO_STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"

CHUNK_SIZE = 2 * 1024 * 1024  # 2MB

RESPONSE_OK = 200
RESPONSE_PARTIAL_CONTENT = 206
RESPONSE_CREATED = 201


def get_max_video_duration(access_token):
    response = requests.post(url=CREATOR_INFO_URL, headers={
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
    })
    return response.json()["data"]["max_video_post_duration_sec"]


def upload_video(tiktok_access_token, max_video_duration, tiktok_title, videotmpfile, tiktok_privacy_status, mime):
    """Posts video with caption."""

    video_size = os.path.getsize(videotmpfile)
    data = {
        "post_info": {
            "title": tiktok_title,
            "privacy_level": tiktok_privacy_status,
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
            "video_cover_timestamp_ms": 0,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": video_size,
            "chunk_size": CHUNK_SIZE,
            "total_chunk_count": max(video_size // CHUNK_SIZE, 1),
        },
    }

    response = requests.post(
        url=DIRECT_POST_URL,
        headers={
            "Authorization": f"Bearer {tiktok_access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        data=data
    )

    upload_url = response.json()["data"]["upload_url"]
    publish_id = response.json()["data"]["publish_id"]

    first_byte = 0
    while first_byte < video_size:
        end_byte = min(first_byte + CHUNK_SIZE - 1, video_size)

        uploads = requests.put(
            url=upload_url,
            headers={
                "Content-Range": f"bytes {first_byte}-{end_byte}/{video_size}",
                "Content-Length": f"{video_size}",
                "Content-Type": f"{mime}",
            },
            data=videotmpfile
        )

        if uploads.status_code not in [RESPONSE_PARTIAL_CONTENT, RESPONSE_CREATED]:
            break

        first_byte = end_byte

    status = requests.post(
        url=GET_VIDEO_STATUS_URL,
        headers={
            "Authorization": f"Bearer {tiktok_access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        data={"publish_id": publish_id},
    )
    return status.json()["data"]


def post(tiktok_access_token, max_video_duration, tiktok_video, tiktok_title, tiktok_privacy_status):

    if not tiktok_video or not tiktok_title:
        raise Exception('No --tiktok-video or --tiktok-title provided.')

    _, videotmpfile = tempfile.mkstemp(prefix='status-video-url-', suffix='.bin')

    with open(videotmpfile, 'wb') as i:
        request = Request(url=tiktok_video, headers={'User-Agent': f'Agoras/{__version__}'})
        imgcontent = urlopen(request).read()
        i.write(imgcontent)

    kind = filetype.guess(videotmpfile)

    if not kind:
        raise Exception(f'Invalid image type for {tiktok_video}')

    if kind.mime not in ['video/quicktime', 'video/mp4', 'video/webm']:
        raise Exception(f'Invalid video type "{kind.mime}" for {tiktok_video}')

    response = upload_video(tiktok_access_token, max_video_duration, tiktok_title, videotmpfile,
                            tiktok_privacy_status, kind.mime)
    status = {
        "id": response.id
    }
    print(json.dumps(status, separators=(',', ':')))


def like():
    raise Exception('like not supported for tiktok')


def delete():
    raise Exception('delete not supported for tiktok')


def share():
    raise Exception('share not supported for tiktok')


def last_from_feed(tiktok_access_token, max_video_duration, tiktok_privacy_status,
                   feed_url, max_count, post_lookback):

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

        title = item.title or ''

        tiktok_title = unescape(title) if title else ''

        try:
            tiktok_video = item.enclosures[0].url
        except Exception:
            tiktok_video = ''

        count += 1
        post(tiktok_access_token, max_video_duration, tiktok_video,
             tiktok_title, tiktok_privacy_status)


def random_from_feed(tiktok_access_token, max_video_duration, tiktok_privacy_status,
                     feed_url, max_post_age):

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
            'date': item.pub_date
        }

        try:
            json_index_content[str(item_timestamp)]['image'] = item.enclosures[0].url
        except Exception:
            json_index_content[str(item_timestamp)]['image'] = ''

    random_status_id = random.choice(list(json_index_content.keys()))
    random_status_title = json_index_content[random_status_id]['title']
    tiktok_video = json_index_content[random_status_id]['image']

    tiktok_title = unescape(random_status_title) if random_status_title else ''

    post(tiktok_access_token, max_video_duration, tiktok_video, tiktok_title,
         tiktok_privacy_status)


def schedule(tiktok_access_token, max_video_duration, google_sheets_id,
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

        tiktok_title, tiktok_privacy_status, tiktok_video, \
            date, hour, state = row

        newcontent.append([
            tiktok_title, tiktok_privacy_status, tiktok_video,
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
        post(tiktok_access_token, max_video_duration, tiktok_video,
             tiktok_title, tiktok_privacy_status)

    worksheet.clear()

    for row in newcontent:
        worksheet.append_row(row, table_range='A1')


def main(kwargs):

    action = kwargs.get('action')
    tiktok_access_token = kwargs.get('tiktok_access_token', None) or \
        os.environ.get('TIKTOK_ACCESS_TOKEN', None)
    tiktok_title = kwargs.get('tiktok_title', '') or \
        os.environ.get('TIKTOK_TITLE', '')
    tiktok_privacy_status = kwargs.get('tiktok_privacy_status', '') or \
        os.environ.get('TIKTOK_PRIVACY_STATUS', '')
    tiktok_video = kwargs.get('tiktok_video', '') or \
        os.environ.get('TIKTOK_VIDEO', '')
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

    max_video_duration = get_max_video_duration(tiktok_access_token)

    if action == 'post':
        post(tiktok_access_token, max_video_duration, tiktok_video,
             tiktok_title, tiktok_privacy_status)
    elif action == 'like':
        like()
    elif action == 'share':
        share()
    elif action == 'delete':
        delete()
    elif action == 'last-from-feed':
        last_from_feed(tiktok_access_token, max_video_duration, tiktok_privacy_status,
                       feed_url, max_count, post_lookback)
    elif action == 'random-from-feed':
        random_from_feed(tiktok_access_token, max_video_duration, tiktok_privacy_status,
                         feed_url, max_post_age)
    elif action == 'schedule':
        schedule(tiktok_access_token, max_video_duration, google_sheets_id,
                 google_sheets_name, google_sheets_client_email,
                 google_sheets_private_key, max_count)
    elif action == '':
        raise Exception('--action is a required argument.')
    else:
        raise Exception(f'"{action}" action not supported.')
