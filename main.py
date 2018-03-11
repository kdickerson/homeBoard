from home_board import weather, calendar, special_events, compositor, util
import datetime
import pytz
import os
import sys

TIME_ZONE = "America/Los_Angeles"

def make_image():
    days = ['today', 'plus_one', 'plus_two', 'plus_three']
    context = {day: {'conditions': None, 'forecast': None, 'events': [], 'special_event': None} for day in days}
    tz = pytz.timezone(TIME_ZONE)
    context['now'] = tz.localize(datetime.datetime.now())
    context['today']['date'] = context['now'].date()
    context['plus_one']['date'] = context['today']['date'] + datetime.timedelta(days=1)
    context['plus_two']['date'] = context['today']['date'] + datetime.timedelta(days=2)
    context['plus_three']['date'] = context['today']['date'] + datetime.timedelta(days=3)

    try:
        conditions = weather.fetch() # weather can only fetch conditions and forecast for "now"
        context['today']['conditions'] = conditions['current']
        for day in days:
            context[day]['forecast'] = conditions['forecast'][day]
    except Exception as ex:
        print('Exception while fetching Weather')
        print(ex)

    try:
        calender_events = calendar.fetch(context['now'])
        for day in days:
            context[day]['events'] = calender_events[day]
    except Exception as ex:
        print('Exception while fetching Calendar')
        print(ex)

    try:
        special_event = special_events.fetch(context['today']['date'])
        for day in days:
            context[day]['special_event'] = special_event[day]
            if special_event[day] and day is not 'today':
                context[day]['events'].insert(0, {
                    'calendar_label': '',
                    'all_day': True,
                    'description': special_event[day]['title'],
                    'underway': False,
                })
    except Exception as ex:
        print('Exception while fetching Special Events')
        print(ex)
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
