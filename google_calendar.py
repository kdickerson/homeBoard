# Fetch calendaring info from Google, process, and return
import ast
import datetime
import dateutil.parser
import httplib2
import os
import pytz
from util import local_file

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'google_calendar.key'
CREDENTIALS_FILE = 'google_calendar_credentials.key'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'
TIME_ZONE = "America/Los_Angeles"
MOCK_GOOGLE_CALENDAR_DATA = True
MOCK_GOOGLE_CALENDAR_DATA_FILE = 'mock_google_calendar_data.py.txt'

def _get_credentials_store():
    credential_path = local_file(CREDENTIALS_FILE)
    return Storage(credential_path)

def _get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Must be run in an environment with a browser available to authorize the access.

    Returns:
        Credentials, the obtained credential.
    """
    store = _get_credentials_store()
    credentials = store.get()
    if not credentials or credentials.invalid:
        raise ValueError("No valid credentials found.  Run generate_credentials manually to generate them.")
    return credentials

def _request_data(tz_aware_when):
    if MOCK_GOOGLE_CALENDAR_DATA:
        with open(local_file(MOCK_GOOGLE_CALENDAR_DATA_FILE)) as mock_data:
            eventsResult = ast.literal_eval(mock_data.read())
    else:
        credentials = _get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)
        cur_time = tz_aware_when.astimezone(pytz.utc).isoformat()
        end_of_day = tz_aware_when.replace(hour=23, minute=59, second=59, microsecond=999999).astimezone(pytz.utc).isoformat()
        eventsResult = service.events().list(calendarId='primary', timeMin=cur_time, timeMax=end_of_day, maxResults=10, singleEvents=True, orderBy='startTime').execute()
    return eventsResult.get('items', [])

def _calendar_data(tz_aware_when):
    events = _request_data(tz_aware_when)
    cleaned_events = []
    for event in events:
        cleaned_events.append({
            'start': dateutil.parser.parse(event['start'].get('dateTime', event['start'].get('date'))),
            'description': event['summary']
        })
    return cleaned_events

def fetch():
    tz = pytz.timezone(TIME_ZONE)
    now = tz.localize(datetime.datetime.now())
    plus_one = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    plus_two = plus_one + datetime.timedelta(days=1)
    plus_three = plus_two + datetime.timedelta(days=1)
    return {
        'today': _calendar_data(now),
        'plus_one': _calendar_data(plus_one),
        'plus_two': _calendar_data(plus_two),
        'plus_three': _calendar_data(plus_three)
    }

def generate_credentials():
    '''Requires web browser available to handle authorization flow'''
    store = _get_credentials_store()
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
