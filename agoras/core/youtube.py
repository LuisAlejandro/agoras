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
import time
import random
import tempfile
from html import unescape
from urllib.request import Request, urlopen
import http.client as httplib

import httplib2
import filetype
import gspread
from atoma import parse_rss_bytes
from dateutil import parser
from google.oauth2.service_account import Credentials
from apiclient import discovery
from apiclient import errors
from apiclient import http
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

from agoras import __version__


httplib2.RETRIES = 1


def get_authenticated_service(youtube_project_id, youtube_client_id, youtube_client_secret):
    _, storagefile = tempfile.mkstemp(prefix='storage-', suffix='.json')
    _, secretsfile = tempfile.mkstemp(prefix='secrets-', suffix='.json')

    with open(secretsfile, 'w') as i:
        i.write(json.dumps({
            "web": {
                "project_id": youtube_project_id,
                "client_id": youtube_client_id,
                "client_secret": youtube_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            }
        }))

    flow = flow_from_clientsecrets(secretsfile,
                                   scope="https://www.googleapis.com/auth/youtube.upload")

    storage = Storage(storagefile)
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage)

    return discovery.build("youtube", "v3", http=credentials.authorize(httplib2.Http()))


def upload_video(client, youtube_title, youtube_description, youtube_video, youtube_category_id,
                 youtube_privacy_status, youtube_keywords):

    # Maximum number of times to retry before giving up.
    MAX_RETRIES = 10

    # Always retry when these exceptions are raised.
    RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
                            httplib.IncompleteRead, httplib.ImproperConnectionState,
                            httplib.CannotSendRequest, httplib.CannotSendHeader,
                            httplib.ResponseNotReady, httplib.BadStatusLine)

    # Always retry when an apiclient.errors.HttpError with one of these status
    # codes is raised.
    RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

    retry = 0
    response = None
    error = None
    tags = None

    if youtube_keywords:
        tags = youtube_keywords.split(",")

    body = dict(
        snippet=dict(
            title=youtube_title,
            description=youtube_description,
            tags=tags,
            categoryId=youtube_category_id
        ),
        status=dict(
            privacyStatus=youtube_privacy_status
        )
    )

    # Call the API's videos.insert method to create and upload the video.
    request = client.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=http.MediaFileUpload(youtube_video, chunksize=-1, resumable=True)
    )

    while response is None:
        try:
            print("Uploading file...")
            _, response = request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print("Video id '%s' was successfully uploaded." % response['id'])
                else:
                    raise Exception("The upload failed with an unexpected response: %s" % response)

        except errors.HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
            else:
                raise

        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)

    return response


def post(client, youtube_title, youtube_description, youtube_video, youtube_category_id,
         youtube_privacy_status, youtube_keywords):

    if not youtube_title or not youtube_video:
        raise Exception('No --youtube-title or --youtube-video provided.')

    _, videotmpfile = tempfile.mkstemp(prefix='status-video-url-', suffix='.bin')

    with open(videotmpfile, 'wb') as i:
        request = Request(url=youtube_video, headers={'User-Agent': f'Agoras/{__version__}'})
        imgcontent = urlopen(request).read()
        i.write(imgcontent)

    kind = filetype.guess(videotmpfile)

    if not kind:
        raise Exception(f'Invalid image type for {youtube_video}')

    if kind.mime not in ['video/quicktime', 'video/mp4', 'video/webm']:
        raise Exception(f'Invalid video type "{kind.mime}" for {youtube_video}')

    response = upload_video(client, youtube_title, youtube_description, videotmpfile, youtube_category_id,
                            youtube_privacy_status, youtube_keywords)
    status = {
        "id": response.id
    }
    print(json.dumps(status, separators=(',', ':')))


def like(client, youtube_video_id):
    request = client.videos().rate(
        id=youtube_video_id,
        rating="like"
    )
    request.execute()


def delete(client, youtube_video_id):
    request = client.videos().delete(
        id=youtube_video_id
    )
    request.execute()


def share():
    raise Exception('share not supported for youtube')


def last_from_feed(client, youtube_description, youtube_category_id,
                   youtube_privacy_status, youtube_keywords,
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

        youtube_title = unescape(title) if title else ''

        try:
            youtube_video = item.enclosures[0].url
        except Exception:
            youtube_video = ''

        count += 1
        post(client, youtube_title, youtube_description, youtube_category_id,
             youtube_privacy_status, youtube_video, youtube_keywords)


def random_from_feed(client, youtube_description, youtube_category_id,
                     youtube_privacy_status, youtube_keywords, feed_url,
                     max_post_age):

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
            json_index_content[str(item_timestamp)]['video'] = item.enclosures[0].url
        except Exception:
            json_index_content[str(item_timestamp)]['video'] = ''

    random_status_id = random.choice(list(json_index_content.keys()))
    random_status_title = json_index_content[random_status_id]['title']
    youtube_video = json_index_content[random_status_id]['video']

    youtube_title = unescape(random_status_title) if random_status_title else ''

    post(client, youtube_title, youtube_description, youtube_category_id,
         youtube_privacy_status, youtube_video, youtube_keywords)


def schedule(client, google_sheets_id,
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

        youtube_title, youtube_description, youtube_category_id, \
            youtube_privacy_status, youtube_video, youtube_keywords, \
            date, hour, state = row

        newcontent.append([
            youtube_title, youtube_description, youtube_category_id,
            youtube_privacy_status, youtube_video, youtube_keywords,
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
        post(client, youtube_title, youtube_description, youtube_category_id,
             youtube_privacy_status, youtube_video, youtube_keywords)

    worksheet.clear()

    for row in newcontent:
        worksheet.append_row(row, table_range='A1')


def main(kwargs):

    action = kwargs.get('action')
    youtube_project_id = kwargs.get('youtube_project_id', '') or \
        os.environ.get('YOUTUBE_PROJECT_ID', '')
    youtube_client_id = kwargs.get('youtube_client_id', '') or \
        os.environ.get('YOUTUBE_CLIENT_ID', '')
    youtube_client_secret = kwargs.get('youtube_client_secret', '') or \
        os.environ.get('YOUTUBE_CLIENT_SECRET', '')
    youtube_video_id = kwargs.get('youtube_video_id', None) or \
        os.environ.get('YOUTUBE_VIDEO_ID', None)
    youtube_title = kwargs.get('youtube_title', '') or \
        os.environ.get('YOUTUBE_TITLE', '')
    youtube_description = kwargs.get('youtube_description', '') or \
        os.environ.get('YOUTUBE_DESCRIPTION', '')
    youtube_category_id = kwargs.get('youtube_category_id', '') or \
        os.environ.get('YOUTUBE_CATEGORY_ID', '')
    youtube_privacy_status = kwargs.get('youtube_privacy_status', '') or \
        os.environ.get('YOUTUBE_PRIVACY_STATUS', '')
    youtube_video = kwargs.get('youtube_video', '') or \
        os.environ.get('YOUTUBE_VIDEO', '')
    youtube_keywords = kwargs.get('youtube_keywords', '') or \
        os.environ.get('YOUTUBE_KEYWORDS', '')
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

    client = get_authenticated_service(youtube_project_id, youtube_client_id, youtube_client_secret)

    if action == 'post':
        post(client, youtube_title, youtube_description, youtube_category_id,
             youtube_privacy_status, youtube_video, youtube_keywords)
    elif action == 'like':
        like(client, youtube_video_id)
    elif action == 'share':
        share()
    elif action == 'delete':
        delete(client, youtube_video_id)
    elif action == 'last-from-feed':
        last_from_feed(client, youtube_description, youtube_category_id,
                       youtube_privacy_status, youtube_keywords,
                       feed_url, max_count, post_lookback)
    elif action == 'random-from-feed':
        random_from_feed(client, youtube_description, youtube_category_id,
                         youtube_privacy_status, youtube_keywords, feed_url,
                         max_post_age)
    elif action == 'schedule':
        schedule(client, google_sheets_id,
                 google_sheets_name, google_sheets_client_email,
                 google_sheets_private_key, max_count)
    elif action == '':
        raise Exception('--action is a required argument.')
    else:
        raise Exception(f'"{action}" action not supported.')
