# Fetch calendaring info from Google, process, and return
import datetime
import dateutil.parser
import httplib2
import json
import logging
import os
import pytz
from .util import local_file

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# If modifying these scopes, delete your previously saved credentials
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'private/google_calendar.key'
CREDENTIALS_FILE = 'private/google_calendar_credentials.key'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'
MOCK_GOOGLE_CALENDAR_DATA = False
MOCK_GOOGLE_CALENDAR_DATA_FILE = 'mock_data/mock_google_calendar_data.json'

# For Google's Discovery service, which is suddenly really slow and I need to stop hitting it for every calendar request
class MemoryCache(Cache):
    _CACHE = {}

    def get(self, url):
        return MemoryCache._CACHE.get(url)

    def set(self, url, content):
        MemoryCache._CACHE[url] = content


# See list_calendars() to get a list of available IDs
CALENDARS = [
    {'id': 'kyle.dickerson@gmail.com', 'label': 'Kyle'},
    {'id': 'dickersonjess@gmail.com', 'label': 'Jess'},
    {'id': 'hj0q4jnosi4jm2mhpecd2b9564@group.calendar.google.com', 'label': 'Heather'},
    {'id': 'jpsmb71hrr2fvqo3l9ffpo3ca8@group.calendar.google.com', 'label': 'Corinne'},
    {'id': 'gdh9plpc638531bfj3epe7gal8@group.calendar.google.com', 'label': 'LLNL'},
    {'id': '61bo389o9ge3gaaog289vjn32o@group.calendar.google.com', 'label': 'Rancho'},
    {'id': 'pd8j83mj5r8n5abdgil181ook8@group.calendar.google.com', 'label': 'Vacation'},
    {'id': 'en.usa#holiday@group.v.calendar.google.com', 'label': 'Holidays'}
]

def _get_credentials_store():
    logging.debug('_get_credentials_store')
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
    logging.debug('_get_credentials')
    store = _get_credentials_store()
    credentials = store.get()
    if not credentials:
        raise ValueError("No valid credentials found.  Run generate_credentials manually to generate them.  Must be done manually with available local web browser the first time only.")
    if credentials.invalid:
        credentials = generate_credentials()
    return credentials

def _request_data(tz_aware_when, calendar, timezone):
    logging.debug('_request_data:start')
    if MOCK_GOOGLE_CALENDAR_DATA:
        with open(local_file(MOCK_GOOGLE_CALENDAR_DATA_FILE)) as mock_data:
            eventsResult = json.load(mock_data)[calendar['id']]
    else:
        credentials = _get_credentials()
        http = credentials.authorize(httplib2.Http(timeout=60))
        logging.debug('_request_data:discovery start')
        service = discovery.build('calendar', 'v3', http=http, cache=MemoryCache())
        logging.debug('_request_data:discovery end')
        # Issues with all-day events not being returned by Google after the UTC date rolls over to tomorrow, even though the local time is still today
        # So we'll just ask for everything today, and filter it locally.  Not great, but I'm not seeing a better solution
        start_of_day = tz_aware_when.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc).isoformat()
        end_of_day = tz_aware_when.replace(hour=23, minute=59, second=59, microsecond=999999).astimezone(pytz.utc).isoformat()
        logging.debug('_request_data:request start')
        eventsResult = service.events().list(calendarId=calendar['id'], timeMin=start_of_day, timeMax=end_of_day, singleEvents=True, orderBy='startTime', timeZone=tz_aware_when.tzinfo.zone).execute()
        logging.debug('_request_data:request end')

    eventsResult['items'] = eventsResult.get('items', [])
    for event in eventsResult['items']:
        event['parsed_start'] = dateutil.parser.parse(event['start']['dateTime']) if 'dateTime' in event['start'] else timezone.localize(dateutil.parser.parse(event['start']['date']))
        event['parsed_end'] = dateutil.parser.parse(event['end']['dateTime']) if 'dateTime' in event['end'] else timezone.localize(dateutil.parser.parse(event['end']['date']))
        event['all_day'] = 'date' in event['start']
    eventsResult['items'] = [e for e in eventsResult['items'] if e['all_day'] or e['parsed_end'] > tz_aware_when]
    logging.debug('_request_data:end')
    return eventsResult['items']

def _calendar_data(tz_aware_when, calendar, timezone):
    events = _request_data(tz_aware_when, calendar, timezone)
    cleaned_events = []
    for event in events:
        cleaned_events.append({
            'calendar_label': calendar['label'],
            'start': event['parsed_start'],
            'end': event['parsed_end'],
            'all_day': event['all_day'],
            'description': event['summary'],
        })
    return cleaned_events

def _fetch_events_for_day(day, calendars, timezone):
    logging.debug('_fetch_events_for_day')
    events = []
    for calendar in calendars:
        events.extend(_calendar_data(day, calendar, timezone))
    events.sort(key=lambda e: e['start'])
    return events

def fetch(tz_aware_when):
    logging.debug('fetch')
    plus_one = tz_aware_when.replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    plus_two = plus_one + datetime.timedelta(days=1)
    plus_three = plus_two + datetime.timedelta(days=1)
    return {
        'today': _fetch_events_for_day(tz_aware_when, CALENDARS, tz_aware_when.tzinfo),
        'plus_one': _fetch_events_for_day(plus_one, CALENDARS, tz_aware_when.tzinfo),
        'plus_two': _fetch_events_for_day(plus_two, CALENDARS, tz_aware_when.tzinfo),
        'plus_three': _fetch_events_for_day(plus_three, CALENDARS, tz_aware_when.tzinfo)
    }

def generate_credentials():
    '''Requires web browser available to handle authorization flow'''
    logging.debug('generate_credentials')
    store = _get_credentials_store()
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(local_file(CLIENT_SECRET_FILE), SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store)
    return credentials

def list_calendars():
    logging.debug('list_calendars')
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
