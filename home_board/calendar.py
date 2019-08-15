# Fetch calendaring info from Google, process, and return
import datetime
import json
import logging

import dateutil.parser
import httplib2
import pytz
from apiclient import discovery
from googleapiclient.discovery_cache.base import Cache
from oauth2client import client, tools
from oauth2client.file import Storage

from .util import local_file

# If modifying these scopes, delete your previously saved credentials
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'private/google_calendar.key'
CREDENTIALS_FILE = 'private/google_calendar_credentials.key'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'
MOCK_GOOGLE_CALENDAR_DATA = False
MOCK_GOOGLE_CALENDAR_DATA_FILE = 'mock_data/mock_google_calendar_data.json'
# TODO: URLs seem to be changing which negates the cache, but fills it up.
#       Need to figure that out and implement a cleanup strategy so old entries get culled
HTTPLIB2_CACHE_DIR = None  # '/ram-tmp/httplib2_cache'


class MemoryCache(Cache):
    '''
        For Google's Discovery service, which is suddenly really slow and
            I need to stop hitting it for every calendar request
    '''
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
    {'id': 'b3qlip954r2ffthscc0r7lunps@group.calendar.google.com', 'label': 'Rancho'},
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
        msg = "No valid credentials found.  \
            Run generate_credentials manually to generate them.  \
            Must be done manually with available local web browser the first time only."
        raise ValueError(msg)
    if credentials.invalid:
        credentials = generate_credentials()
    return credentials


def _request_data(tz_aware_when_start, tz_aware_when_end, calendar, timezone):
    logging.debug('_request_data:start')
    if MOCK_GOOGLE_CALENDAR_DATA:
        with open(local_file(MOCK_GOOGLE_CALENDAR_DATA_FILE)) as mock_data:
            eventsResult = json.load(mock_data)[calendar['id']]
    else:
        credentials = _get_credentials()
        http = credentials.authorize(httplib2.Http(cache=HTTPLIB2_CACHE_DIR, timeout=60))
        logging.debug('_request_data:discovery start')
        service = discovery.build('calendar', 'v3', http=http, cache=MemoryCache())
        logging.debug('_request_data:discovery end')
        start = tz_aware_when_start.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc).isoformat()
        end = tz_aware_when_end.replace(hour=23, minute=59, second=59, microsecond=999999).astimezone(pytz.utc).isoformat()  # noqa: E501
        logging.debug('_request_data:request start')
        eventsResult = service.events().list(
            calendarId=calendar['id'],
            timeMin=start,
            timeMax=end,
            singleEvents=True,
            orderBy='startTime',
            timeZone=timezone
        ).execute()
        logging.debug('_request_data:request end')

    eventsResult['items'] = eventsResult.get('items', [])
    for event in eventsResult['items']:
        event['parsed_start'] = (
            dateutil.parser.parse(event['start']['dateTime']) if 'dateTime' in event['start']
            else timezone.localize(dateutil.parser.parse(event['start']['date']))
        )
        event['parsed_end'] = (
            dateutil.parser.parse(event['end']['dateTime']) if 'dateTime' in event['end']
            else timezone.localize(dateutil.parser.parse(event['end']['date']))
        )
        event['all_day'] = 'date' in event['start']
    logging.debug('_request_data:end')
    return eventsResult['items']


def _calendar_data(tz_aware_when_start, tz_aware_when_end, calendar, timezone):
    events = _request_data(tz_aware_when_start, tz_aware_when_end, calendar, timezone)
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


def _fetch_events(first_day, last_day, calendars, timezone):
    logging.debug('_fetch_events')
    events = []
    for calendar in calendars:
        events.extend(_calendar_data(first_day, last_day, calendar, timezone))
    events.sort(key=lambda e: e['start'])
    return events


def _segment_events(tz_aware_when, today, plus_one, plus_two, plus_three, events):
    """
    >>> tz = pytz.timezone("America/Los_Angeles")
    >>> tz_aware_when = dateutil.parser.parse("2018-12-01T18:32:45-08:00")
    >>> today = tz_aware_when.replace(hour=0, minute=0, second=0, microsecond=0)
    >>> plus_one = today + datetime.timedelta(days=1)
    >>> plus_two = plus_one + datetime.timedelta(days=1)
    >>> plus_three = plus_two + datetime.timedelta(days=1)
    >>> events = [
    ...     {
    ...         'start': tz.localize(dateutil.parser.parse('2018-11-30')),
    ...         'end': tz.localize(dateutil.parser.parse('2018-12-04')),
    ...         'description': 'Multi-day',
    ...         'all_day': True,
    ...     },
    ...     {
    ...         'start': dateutil.parser.parse('2018-12-01T18:15:00-08:00'),
    ...         'end': dateutil.parser.parse('2018-12-01T19:00:00-08:00'),
    ...         'description': 'Happening Now',
    ...         'all_day': False,
    ...     },
    ...     {
    ...         'start': dateutil.parser.parse('2018-12-01T20:00:00-08:00'),
    ...         'end': dateutil.parser.parse('2018-12-01T20:30:00-08:00'),
    ...         'description': 'Future still Today',
    ...         'all_day': False,
    ...     },
    ...     {
    ...         'start': dateutil.parser.parse('2018-12-02T08:00:00-08:00'),
    ...         'end': dateutil.parser.parse('2018-12-02T09:00:00-08:00'),
    ...         'description': 'Tomorrow',
    ...         'all_day': False,
    ...     },
    ...     {
    ...         'start': tz.localize(dateutil.parser.parse('2018-12-03')),
    ...         'end': tz.localize(dateutil.parser.parse('2018-12-06')),
    ...         'description': 'Future past the end',
    ...         'all_day': True,
    ...     },
    ...     {
    ...         'start': dateutil.parser.parse('2018-12-01T08:00:00-08:00'),
    ...         'end': dateutil.parser.parse('2018-12-01T11:00:00-08:00'),
    ...         'description': 'Already Over',
    ...         'all_day': False,
    ...     },
    ... ]
    >>> segmented_events = _segment_events(tz_aware_when, today, plus_one, plus_two, plus_three, events)
    >>> len(segmented_events['today'])
    3
    >>> segmented_events['today'][0]['description']
    'Multi-day'
    >>> segmented_events['today'][1]['description']
    'Happening Now'
    >>> segmented_events['today'][2]['description']
    'Future still Today'
    >>> len(segmented_events['plus_one'])
    2
    >>> segmented_events['plus_one'][0]['description']
    'Multi-day'
    >>> segmented_events['plus_one'][1]['description']
    'Tomorrow'
    >>> len(segmented_events['plus_two'])
    2
    >>> segmented_events['plus_two'][0]['description']
    'Multi-day'
    >>> segmented_events['plus_two'][1]['description']
    'Future past the end'
    >>> len(segmented_events['plus_three'])
    1
    >>> segmented_events['plus_three'][0]['description']
    'Future past the end'
    >>>
    """
    retVal = {'today': [], 'plus_one': [], 'plus_two': [], 'plus_three': []}
    for event in events:
        if event['end'] < tz_aware_when:
            continue  # Skip events that are already over
        if event['start'] < plus_one and event['end'] > today:
            retVal['today'].append(event)
        if event['start'] < plus_two and event['end'] > plus_one:
            retVal['plus_one'].append(event)
        if event['start'] < plus_three and event['end'] > plus_two:
            retVal['plus_two'].append(event)
        if event['end'] > plus_three:
            retVal['plus_three'].append(event)
    return retVal


def fetch(tz_aware_when):
    logging.debug('fetch')
    today = tz_aware_when.replace(hour=0, minute=0, second=0, microsecond=0)
    plus_one = today + datetime.timedelta(days=1)
    plus_two = plus_one + datetime.timedelta(days=1)
    plus_three = plus_two + datetime.timedelta(days=1)
    fetched_events = _fetch_events(today, plus_three, CALENDARS, tz_aware_when.tzinfo)
    return _segment_events(tz_aware_when, today, plus_one, plus_two, plus_three, fetched_events)


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
