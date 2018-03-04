# Fetch calendaring info from Google, process, and return
import ast
import datetime
import dateutil.parser
import httplib2
import os
import pytz
from .util import local_file

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = '../private/google_calendar.key'
CREDENTIALS_FILE = '../private/google_calendar_credentials.key'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'
TIME_ZONE = "America/Los_Angeles"
MOCK_GOOGLE_CALENDAR_DATA = False
MOCK_GOOGLE_CALENDAR_DATA_FILE = '../mock_data/mock_google_calendar_data.py.txt'

# See list_calendars() to get a list of available IDs
CALENDARS = [
    {'id': 'kyle.dickerson@gmail.com', 'label': 'Kyle'},
    {'id': 'dickersonjess@gmail.com', 'label': 'Jess'},
    {'id': 'hj0q4jnosi4jm2mhpecd2b9564@group.calendar.google.com', 'label': 'Heather'},
    {'id': 'jpsmb71hrr2fvqo3l9ffpo3ca8@group.calendar.google.com', 'label': 'Corinne'},
    {'id': 'gdh9plpc638531bfj3epe7gal8@group.calendar.google.com', 'label': 'LLNL'},
    {'id': '18beqncm6ftugft30sfb23epjg@group.calendar.google.com', 'label': 'Rancho'},
]

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

def _request_data(tz_aware_when, calendar):
    if MOCK_GOOGLE_CALENDAR_DATA:
        with open(local_file(MOCK_GOOGLE_CALENDAR_DATA_FILE)) as mock_data:
            eventsResult = ast.literal_eval(mock_data.read())
    else:
        credentials = _get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('calendar', 'v3', http=http)
        cur_time = tz_aware_when.astimezone(pytz.utc).isoformat()
        end_of_day = tz_aware_when.replace(hour=23, minute=59, second=59, microsecond=999999).astimezone(pytz.utc).isoformat()
        eventsResult = service.events().list(calendarId=calendar['id'], timeMin=cur_time, timeMax=end_of_day, maxResults=10, singleEvents=True, orderBy='startTime').execute()
    return eventsResult.get('items', [])

def _calendar_data(tz_aware_when, calendar, timezone):
    events = _request_data(tz_aware_when, calendar)
    cleaned_events = []
    for event in events:
        cleaned_events.append({
            'calendar_label': calendar['label'],
            'start': dateutil.parser.parse(event['start']['dateTime']) if 'dateTime' in event['start'] else timezone.localize(dateutil.parser.parse(event['start']['date'])),
            'all_day': 'date' in event['start'],
            'description': event['summary'],
        })
    return cleaned_events

def _fetch_events_for_day(day, calendars, timezone):
    events = []
    for calendar in calendars:
        events.extend(_calendar_data(day, calendar, timezone))
    events.sort(key=lambda e: e['start'])
    return events

def fetch():
    tz = pytz.timezone(TIME_ZONE)
    now = tz.localize(datetime.datetime.now())
    plus_one = now.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    plus_two = plus_one + datetime.timedelta(days=1)
    plus_three = plus_two + datetime.timedelta(days=1)
    return {
        'today': _fetch_events_for_day(now, CALENDARS, tz),
        'plus_one': _fetch_events_for_day(plus_one, CALENDARS, tz),
        'plus_two': _fetch_events_for_day(plus_two, CALENDARS, tz),
        'plus_three': _fetch_events_for_day(plus_three, CALENDARS, tz)
    }

def generate_credentials():
    '''Requires web browser available to handle authorization flow'''
    store = _get_credentials_store()
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)

def list_calendars():
    credentials = _get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    calendar_list = service.calendarList().list().execute()
    cleaned_calendars = []
    for item in calendar_list.get('items', []):
        cleaned_calendars.append({
            'id': item['id'],
            'summary': item.get('summaryOverride', item['summary']),
            'description': item.get('description', ''),
        })
    return cleaned_calendars
