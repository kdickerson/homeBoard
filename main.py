from home_board import weather, calendar, special_events, compositor, util
import datetime
import os
import pickle
import pytz
import sys

TIME_ZONE = "America/Los_Angeles"
SAVE_MOCK = False
MOCK_CALENDAR = False
MOCK_WEATHER = False
MOCK_SPECIAL_EVENTS = False
MOCK_CALENDAR_FILE = 'mock_data/mock_calendar_data.pickle'
MOCK_WEATHER_FILE = 'mock_data/mock_weather_data.pickle'
MOCK_SPECIAL_EVENTS_FILE = 'mock_data/mock_special_events_data.pickle'

def _dst_start_end(tz_aware_when):
    dst_start_utc, dst_end_utc = [dt for dt in tz_aware_when.tzinfo._utc_transition_times if dt.year == tz_aware_when.year]
    dst_start_tran_info = tz_aware_when.tzinfo._transition_info[tz_aware_when.tzinfo._utc_transition_times.index(dst_start_utc)]
    dst_end_tran_info = tz_aware_when.tzinfo._transition_info[tz_aware_when.tzinfo._utc_transition_times.index(dst_end_utc)]
    dst_start_local = tz_aware_when.tzinfo.localize(dst_start_utc + dst_start_tran_info[0])
    dst_end_local = tz_aware_when.tzinfo.localize(dst_end_utc + dst_end_tran_info[0])
    return dst_start_local, dst_end_local

def fetch_calendar(context, days):
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
    except Exception as ex:
        print('Exception while fetching Calendar')
        print(ex)

def fetch_weather(context, days):
    try:
        if MOCK_WEATHER:
            with open(util.local_file(MOCK_WEATHER_FILE), 'rb') as mock_data:
                conditions = pickle.load(mock_data)
        else:
            conditions = weather.fetch() # weather can only fetch conditions and forecast for "now"
            if SAVE_MOCK:
                with open(util.local_file(MOCK_WEATHER_FILE), 'wb') as mock_data:
                    pickle.dump(conditions, mock_data)
        context['today']['conditions'] = conditions['current']
        for day in days:
            context[day]['forecast'] = conditions['forecast'][day]
    except Exception as ex:
        print('Exception while fetching Weather')
        print(ex)

def fetch_special_events(context, days):
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
            if special_event[day] and 'title' in special_event[day] and (day != 'today' or 'msg' not in special_event[day]):
                context[day]['events'].insert(0, {
                    'calendar_label': special_event[day]['header'] if special_event[day]['header'] else '',
                    'all_day': True,
                    'description': special_event[day]['title'],
                    'underway': False,
                })
    except Exception as ex:
        print('Exception while fetching Special Events')
        print(ex)

def fetch_daylight_saving_time(context, days):
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
    except Exception as ex:
        print('Exception while processing Daylight Saving Time')
        print(ex)

def fetch_data():
    days = ['today', 'plus_one', 'plus_two', 'plus_three']
    context = {day: {'conditions': None, 'forecast': None, 'events': [], 'special_event': None} for day in days}
    tz = pytz.timezone(TIME_ZONE)
    context['now'] = tz.localize(datetime.datetime.now())
    context['today']['date'] = context['now'].date()
    context['plus_one']['date'] = context['today']['date'] + datetime.timedelta(days=1)
    context['plus_two']['date'] = context['today']['date'] + datetime.timedelta(days=2)
    context['plus_three']['date'] = context['today']['date'] + datetime.timedelta(days=3)

    fetch_weather(context, days)
    fetch_calendar(context, days)
    fetch_special_events(context, days)
    #fetch_daylight_saving_time(context, days)
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

'''
    Save image rather than send to display (for quick testing of design changes):
    python main.py save
'''
if __name__ == '__main__':
    util.set_base_path(os.path.dirname(os.path.abspath(__file__)))

    if len(sys.argv) > 1 and sys.argv[1] == 'save':
        save_image()
    else:
        display_image()
