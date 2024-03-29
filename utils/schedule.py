import sys
import datetime

import gspread
from google.oauth2.service_account import Credentials


google_sheets_id = sys.argv[1]
google_sheets_name = sys.argv[2]
google_sheets_client_email = sys.argv[3]
google_sheets_private_key = sys.argv[4]

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
       'manage your social networks?')

creds = Credentials.from_service_account_info(account_info,
                                              scopes=gspread_scope)
gclient = gspread.authorize(creds)
spreadsheet = gclient.open_by_key(google_sheets_id)

worksheet = spreadsheet.worksheet(google_sheets_name)

worksheet.append_row([msg,
                      'https://luisalejandro.org/blog/posts/nuevo-blog',
                      '',
                      '',
                      '',
                      '',
                      currdate,
                      currhour,
                      'draft'], table_range='A1')
