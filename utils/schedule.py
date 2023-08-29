import os
import datetime

import gspread
from google.oauth2.service_account import Credentials


google_sheets_id = os.environ.get('GOOGLE_SHEETS_ID', '')
google_sheets_name = os.environ.get('GOOGLE_SHEETS_NAME', '')
google_sheets_client_email = os.environ.get('GOOGLE_SHEETS_CLIENT_EMAIL', '')
google_sheets_private_key = os.environ.get('GOOGLE_SHEETS_PRIVATE_KEY', '')

gspread_scope = ['https://spreadsheets.google.com/feeds']
account_info = {
    'private_key': google_sheets_private_key.replace('\\n', '\n'),
    'client_email': google_sheets_client_email,
    'token_uri': 'https://oauth2.googleapis.com/token',
}

now = datetime.datetime.now()
currdate = now.strftime('%d-%m-%Y')
currhour = now.strftime('%H')
msg = ('Have you heard of Agoras, a command line python utility to '
       'manage your social networks? https://github.com/LuisAlejandro/agoras')

creds = Credentials.from_service_account_info(account_info,
                                              scopes=gspread_scope)
gclient = gspread.authorize(creds)
spreadsheet = gclient.open_by_key(google_sheets_id)

worksheet = spreadsheet.worksheet(google_sheets_name)

worksheet.append_row([msg,
                      'https://imgix.cosmicjs.com/ea592bb0-3eb1-11ee-82b2-d53af1858037-Untitled.png',
                      '',
                      '',
                      '',
                      currdate,
                      currhour,
                      'draft'])
