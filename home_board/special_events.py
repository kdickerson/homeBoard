# Fetch special event info (Birthdays, Holidays, Anniversaries, etc. with image)
import datetime

EVENTS = [
    {'month': 3, 'day': 17, 'header': 'Birthday', 'title': 'Corinne', 'msg': 'Happy Birthday, Corinne!', 'icon': 'birthday'},
    {'month': 6, 'day': 9, 'header': 'Birthday', 'title': 'Kyle', 'msg': 'Happy Birthday, Kyle!', 'icon': 'birthday'},
    {'month': 6, 'day': 23, 'header': 'Anniversary', 'title': 'Kyle & Jess', 'msg': 'Happy Anniversary!', 'icon': 'birthday'},
    {'month': 9, 'day': 20, 'header': 'Birthday', 'title': 'Jess', 'msg': 'Happy Birthday, Jess!', 'icon': 'birthday'},
    {'month': 10, 'day': 28, 'header': 'Birthday', 'title': 'Heather', 'msg': 'Happy Birthday, Heather!', 'icon': 'birthday'},
    {'month': 10, 'day': 31, 'msg': 'Happy Halloween!', 'icon': 'halloween'},
    {'month': 12, 'day': 25, 'msg': 'Merry Christmas!', 'icon': 'christmas'},
    {'year': 2018, 'month': 11, 'day': 22, 'msg': 'Happy Thanksgiving!', 'icon': 'thanksgiving'},
]

def _find_event_for_day(day):
    return next((e for e in EVENTS if day.month == e['month'] and day.day == e['day'] and ('year' not in e or day.year == e['year'])), None)

def fetch(today):
    #today = datetime.date(2018, 12, 25)
    plus_one = today + datetime.timedelta(days=1)
    plus_two = plus_one + datetime.timedelta(days=1)
    plus_three = plus_two + datetime.timedelta(days=1)
    return {
        'today': _find_event_for_day(today),
        'plus_one': _find_event_for_day(plus_one),
        'plus_two': _find_event_for_day(plus_two),
        'plus_three': _find_event_for_day(plus_three),
    }
