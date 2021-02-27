import collections
import datetime
import logging
import os
import pickle
import sys

import pytz

from home_board import calendar, compositor
from home_board import nws as weather
from home_board import special_events, util

TIME_ZONE = "America/Los_Angeles"
SAVE_MOCK = False
MOCK_CALENDAR = False
MOCK_WEATHER = False
MOCK_SPECIAL_EVENTS = False
MOCK_CALENDAR_FILE = 'mock_data/mock_calendar_data.pickle'
MOCK_WEATHER_FILE = 'mock_data/mock_weather_data.pickle'
MOCK_SPECIAL_EVENTS_FILE = 'mock_data/mock_special_events_data.pickle'
CACHE_FILE = None  # '/ram-tmp/home_board.cache'

logging.basicConfig(level=logging.DEBUG)


def deep_defaults(target, source):
    """
    https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
    Modified to only fill in empty entries in target using values from source
    """
    for k, v in source.items():
        if (k in target and isinstance(target[k], dict) and isinstance(source[k], collections.Mapping)):
            deep_defaults(target[k], source[k])
        elif k not in target or target[k] is None:
            target[k] = source[k]


def _dst_start_end(tz_aware_when):
    dst_start_utc, dst_end_utc = [dt for dt in tz_aware_when.tzinfo._utc_transition_times if dt.year == tz_aware_when.year]  # noqa: E501
    dst_start_tran_info = tz_aware_when.tzinfo._transition_info[tz_aware_when.tzinfo._utc_transition_times.index(dst_start_utc)]  # noqa: E501
    dst_end_tran_info = tz_aware_when.tzinfo._transition_info[tz_aware_when.tzinfo._utc_transition_times.index(dst_end_utc)]  # noqa: E501
    dst_start_local = tz_aware_when.tzinfo.localize(dst_start_utc + dst_start_tran_info[0])
    dst_end_local = tz_aware_when.tzinfo.localize(dst_end_utc + dst_end_tran_info[0])
    return dst_start_local, dst_end_local


def fetch_calendar(context, days) -> None:
    logging.debug('fetch_calendar:start')
    try:
        if MOCK_CALENDAR:
            with open(util.local_file(MOCK_CALENDAR_FILE), 'rb') as mock_data:
                calender_events = pickle.load(mock_data)
        else:
            calender_events = calendar.fetch(context['now'])
            if SAVE_MOCK:
                with open(util.local_file(MOCK_CALENDAR_FILE), 'wb') as mock_data:
                    pickle.dump(calender_events, mock_data)
        for day in days:
            context[day]['events'] = calender_events[day]
            for event in context[day]['events']:
                event['underway'] = event['start'] < context['now'] and context['now'] < event['end']
                event['ending_days_away'] = (event['end'].date() - context[day]['date']).days
        context['success']['calendar'] = True
    except Exception:
        logging.exception('Exception while fetching Calendar')
    logging.debug('fetch_calendar:end')


def fetch_weather(context, days) -> None:
    logging.debug('fetch_weather:start')
    try:
        if MOCK_WEATHER:
            with open(util.local_file(MOCK_WEATHER_FILE), 'rb') as mock_data:
                weather_data = pickle.load(mock_data)
        else:
            weather_data = {'current': None, 'forecast': None}
            try:
                weather_data['current'] = weather.fetch_current_conditions()
            except Exception:
                logging.exception('Exception while fetching Weather conditions.')
            try:
                weather_data['forecast'] = weather.fetch_forecasts()
            except Exception:
                logging.exception('Exception while fetching Weather forecasts.')
            if SAVE_MOCK:
                with open(util.local_file(MOCK_WEATHER_FILE), 'wb') as mock_data:
                    pickle.dump(weather_data, mock_data)
        context['today']['conditions'] = weather_data['current']
        if weather_data['forecast']:
            for day in days:
                context[day]['forecast'] = weather_data['forecast'][day]
        context['success']['weather'] = bool(weather_data['current'] and weather_data['forecast'])
    except Exception:
        logging.exception('Exception while fetching Weather')
    logging.debug('fetch_weather:end')


def fetch_special_events(context, days) -> None:
    logging.debug('fetch_special_events:start')
    try:
        if MOCK_SPECIAL_EVENTS:
            with open(util.local_file(MOCK_SPECIAL_EVENTS_FILE), 'rb') as mock_data:
                special_event = pickle.load(mock_data)
        else:
            special_event = special_events.fetch(context['today']['date'])
            if SAVE_MOCK:
                with open(util.local_file(MOCK_SPECIAL_EVENTS_FILE), 'wb') as mock_data:
                    pickle.dump(special_event, mock_data)
        for day in days:
            context[day]['special_event'] = special_event[day]
            if (
                special_event[day] and
                'title' in special_event[day] and
                (day != 'today' or 'msg' not in special_event[day])
            ):
                context[day]['events'].insert(0, {
                    'calendar_label': special_event[day]['header'] if special_event[day]['header'] else '',
                    'all_day': True,
                    'description': special_event[day]['title'],
                    'underway': day == 'today',
                })
        context['success']['special-events'] = True
    except Exception:
        logging.exception('Exception while fetching Special Events')
    logging.debug('fetch_special_events:end')


def fetch_daylight_saving_time(context, days) -> None:
    logging.debug('fetch_daylight_saving_time:start')
    try:
        dst_start_local, dst_end_local = _dst_start_end(context['now'])
        dst_start_local = dst_start_local.date()
        dst_end_local = dst_end_local.date()
        for day in days:
            if context[day]['date'] == dst_start_local or context[day]['date'] == dst_end_local:
                context[day]['events'].insert(0, {
                    'calendar_label': '',
                    'all_day': True,
                    'description': 'DST ' + ('Starts' if context[day]['date'] == dst_start_local else 'Ends'),
                    'underway': day == 'today',
                })
        context['success']['dst'] = True
    except Exception:
        logging.exception('Exception while processing Daylight Saving Time')
    logging.debug('fetch_daylight_saving_time:end')


def fetch_data():
    days = ['today', 'plus_one', 'plus_two', 'plus_three']
    context = {day: {'conditions': None, 'forecast': None, 'events': [], 'special_event': None} for day in days}
    context['success'] = {'calendar': False, 'weather': False, 'special-events': False, 'dst': False}
    tz = pytz.timezone(TIME_ZONE)
    context['now'] = tz.localize(datetime.datetime.now())
    context['today']['date'] = context['now'].date()
    context['plus_one']['date'] = context['today']['date'] + datetime.timedelta(days=1)
    context['plus_two']['date'] = context['today']['date'] + datetime.timedelta(days=2)
    context['plus_three']['date'] = context['today']['date'] + datetime.timedelta(days=3)

    fetch_weather(context, days)
    fetch_calendar(context, days)
    fetch_special_events(context, days)
    # fetch_daylight_saving_time(context, days)
    context['success']['dst'] = True

    # Use cache to fill in any missing info
    if CACHE_FILE and not all(context['success'].values()):
        try:
            with open(CACHE_FILE, 'rb') as cache_file:
                cache = pickle.load(cache_file)
                for day in days:
                    entry = context[day]
                    cache_entry = cache[day]
                    if not context['success']['calendar'] and cache_entry['events']:
                        deep_defaults(entry['events'], cache_entry['events'])
                    if not context['success']['weather']:
                        if cache_entry['conditions']:
                            deep_defaults(entry['conditions'], cache_entry['conditions'])
                        if cache_entry['forecast']:
                            deep_defaults(entry['forecast'], cache_entry['forecast'])
                    if not context['success']['special-events'] and cache_entry['special_event']:
                        deep_defaults(entry['special_event'], cache_entry['special_event'])
        except:  # noqa: E722
            logging.exception(
                'Exception loading data from cache_file: ' +
                str(CACHE_FILE) +
                '.  Needed data for:' +
                ','.join(sorted([k for k, v in context['success'].items() if not v]))
            )

    # Update cache
    if CACHE_FILE:
        try:
            with open(CACHE_FILE, 'wb') as cache_file:
                pickle.dump(context, cache_file)
        except:  # noqa: E722
            logging.exception('Exception writing data to cache_file: ' + str(CACHE_FILE))

    return context


def make_image():
    context = fetch_data()
    return compositor.create(context)


def display_image():
    from waveshare import epd7in5b
    epd = epd7in5b.EPD()
    epd.init()
    image = make_image()
    epd.display_frame(epd.get_frame_buffer(image))


def save_image():
    image = make_image()
    image.save('composite.bmp')


if __name__ == '__main__':
    '''
        Save image rather than send to display (for quick testing of design changes):
        > python main.py save
    '''
    util.set_base_path(os.path.dirname(os.path.abspath(__file__)))

    if len(sys.argv) > 1 and sys.argv[1] == 'save':
        save_image()
    else:
        display_image()
