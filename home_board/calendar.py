# Fetch calendaring info from CalDav server, process, and return
import datetime
import json
import logging

import caldav
import pytz

from .util import local_file

CAL_DAV_URL = 'https://cloud.serindu.com/remote.php/dav/calendars/'
CREDENTIALS_FILE = 'private/calendar-credentials.json'  # relative to project base

# See list_calendars() to get a list of available IDs
CALENDARS = [
    {'id': 'personal', 'label': 'Kyle'},
    {'id': 'personal_shared_by_jess', 'label': 'Jess'},
    {'id': 'personal_shared_by_heather', 'label': 'Heather'},
    {'id': 'personal_shared_by_corinne', 'label': 'Corinne'},
    {'id': 'llnl-holidays', 'label': 'LLNL'},
    {'id': 'junction-ave', 'label': 'Junction'},
    {'id': 'rancho-las-positas', 'label': 'Rancho'},
    {'id': 'family', 'label': 'Family'},
    {'id': 'lvjusd', 'label': 'LVJUSD'}
]


def _get_credentials():
    with open(local_file(CREDENTIALS_FILE)) as credentials_file:
        return json.load(credentials_file)



def _request_data(tz_aware_when_start, tz_aware_when_end, calendar, timezone):
    logging.debug('_request_data:start')
    start = tz_aware_when_start.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(pytz.utc)
    end = tz_aware_when_end.replace(hour=23, minute=59, second=59, microsecond=999999).astimezone(pytz.utc)
    creds = _get_credentials()
    with caldav.DAVClient(url=CAL_DAV_URL, username=creds['username'], password=creds['password']) as client:
        principal = client.principal()
        calendar = principal.calendar(cal_id=calendar['id'])
        events = calendar.search(
            start=start,
            end=end,
            event=True,
            expand=True,
            sort_keys=['DTSTART'],
        )
    logging.debug('_request_data:end')
    return events


def _normalize_event_time(date_or_datetime, timezone):
    '''Convert datetimes to timezone and convert dates to midnight in timezone'''
    if isinstance(date_or_datetime, datetime.datetime):
        return date_or_datetime.astimezone(timezone)
    return timezone.localize(datetime.datetime(date_or_datetime.year, date_or_datetime.month, date_or_datetime.day))


def _calendar_data(tz_aware_when_start, tz_aware_when_end, calendar, timezone):
    events = _request_data(tz_aware_when_start, tz_aware_when_end, calendar, timezone)
    cleaned_events = []
    for event in events:
        # Can't check if is `date` because `datetime`s are `date`s
        is_all_day = not isinstance(event.vobject_instance.vevent.dtstart.value, datetime.datetime)
        start = _normalize_event_time(event.vobject_instance.vevent.dtstart.value, timezone)
        end = _normalize_event_time(event.vobject_instance.vevent.dtend.value, timezone)

        cleaned_events.append({
            'calendar_label': calendar['label'],
            'start': start,
            'end': end,
            'all_day': is_all_day,
            'description': event.vobject_instance.vevent.summary.value,
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
    >>> tz_aware_when = tz.localize(datetime.datetime(2018, 12, 1, 18, 32, 45))
    >>> today = tz_aware_when.replace(hour=0, minute=0, second=0, microsecond=0)
    >>> plus_one = today + datetime.timedelta(days=1)
    >>> plus_two = plus_one + datetime.timedelta(days=1)
    >>> plus_three = plus_two + datetime.timedelta(days=1)
    >>> events = [
    ...     {
    ...         'start': tz.localize(datetime.datetime(2018, 11, 30)),
    ...         'end': tz.localize(datetime.datetime(2018, 12, 4)),
    ...         'description': 'Multi-day',
    ...         'all_day': True,
    ...     },
    ...     {
    ...         'start': tz.localize(datetime.datetime(2018, 12, 1, 18, 15)),
    ...         'end': tz.localize(datetime.datetime(2018, 12, 1, 19)),
    ...         'description': 'Happening Now',
    ...         'all_day': False,
    ...     },
    ...     {
    ...         'start': tz.localize(datetime.datetime(2018, 12, 1, 20)),
    ...         'end': tz.localize(datetime.datetime(2018, 12, 1, 20, 30)),
    ...         'description': 'Future still Today',
    ...         'all_day': False,
    ...     },
    ...     {
    ...         'start': tz.localize(datetime.datetime(2018, 12, 2, 8)),
    ...         'end': tz.localize(datetime.datetime(2018, 12, 2, 9)),
    ...         'description': 'Tomorrow',
    ...         'all_day': False,
    ...     },
    ...     {
    ...         'start': tz.localize(datetime.datetime(2018, 12, 3)),
    ...         'end': tz.localize(datetime.datetime(2018, 12, 6)),
    ...         'description': 'Future past the end',
    ...         'all_day': True,
    ...     },
    ...     {
    ...         'start': tz.localize(datetime.datetime(2018, 12, 1, 8)),
    ...         'end': tz.localize(datetime.datetime(2018, 12, 1, 11)),
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


def list_calendars():
    logging.debug('list_calendars')
    creds = _get_credentials()
    with caldav.DAVClient(url=CAL_DAV_URL, username=creds['username'], password=creds['password']) as client:
        principal = client.principal()
        calendars = principal.calendars()

    cleaned_calendars = []
    for cal in calendars:
        cleaned_calendars.append({
            'id': cal.id,
            'name': cal.name,
        })
    return cleaned_calendars
