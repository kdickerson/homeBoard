# Fetch special event info (Birthdays, Holidays, Anniversaries, etc. with image)
import datetime

'''
    Entry fields:
    year [optional]: year of event
    month: month of event
    day: day of event
    header [optional]: Will be used as the header of the event entry when displayed on calendar
    title [optional]: Will be used as body of the event entry when displayed on calendar
    msg [optional]: Will be the special banner message displayed on the defined date
    icon [optional]: Will be displayed with the special banner message on the defined date

    If title is defined, event (header/title) will appear on future dates in the calendar
        If msg is defined, event will not appear on "today", instead the special banner message is displayed
        If msg is not defined, event will appear on "today"
'''

EVENTS = [
    # Events with same day every year:
    {'month': 2, 'day': 14, 'msg': 'Happy Valentine\'s Day!', 'icon': 'heart'},
    {'month': 7, 'day': 4, 'msg': 'Happy Independence Day!', 'icon': 'flag'},
    {'month': 10, 'day': 31, 'msg': 'Happy Halloween!', 'icon': 'halloween'},
    {'month': 12, 'day': 25, 'msg': 'Merry Christmas!', 'icon': 'christmas'},
    # Thanksgiving Dates:
    {'year': 2025, 'month': 11, 'day': 27, 'msg': 'Happy Thanksgiving!', 'icon': 'thanksgiving'},
    {'year': 2026, 'month': 11, 'day': 26, 'msg': 'Happy Thanksgiving!', 'icon': 'thanksgiving'},
    {'year': 2027, 'month': 11, 'day': 25, 'msg': 'Happy Thanksgiving!', 'icon': 'thanksgiving'},
    {'year': 2028, 'month': 11, 'day': 23, 'msg': 'Happy Thanksgiving!', 'icon': 'thanksgiving'},
    {'year': 2029, 'month': 11, 'day': 22, 'msg': 'Happy Thanksgiving!', 'icon': 'thanksgiving'},
    {'year': 2030, 'month': 11, 'day': 28, 'msg': 'Happy Thanksgiving!', 'icon': 'thanksgiving'},
    
    # Seasons 2025:
    {'year': 2025, 'month': 3, 'day': 20, 'header': 'Season', 'title': 'Spring'},
    {'year': 2025, 'month': 6, 'day': 20, 'header': 'Season', 'title': 'Summer'},
    {'year': 2025, 'month': 9, 'day': 22, 'header': 'Season', 'title': 'Fall'},
    {'year': 2025, 'month': 12, 'day': 21, 'header': 'Season', 'title': 'Winter'},

    # Seasons 2026:
    {'year': 2026, 'month': 3, 'day': 20, 'header': 'Season', 'title': 'Spring'},
    {'year': 2026, 'month': 6, 'day': 21, 'header': 'Season', 'title': 'Summer'},
    {'year': 2026, 'month': 9, 'day': 22, 'header': 'Season', 'title': 'Fall'},
    {'year': 2026, 'month': 12, 'day': 21, 'header': 'Season', 'title': 'Winter'},

    # Seasons 2027:
    {'year': 2027, 'month': 3, 'day': 20, 'header': 'Season', 'title': 'Spring'},
    {'year': 2027, 'month': 6, 'day': 21, 'header': 'Season', 'title': 'Summer'},
    {'year': 2027, 'month': 9, 'day': 22, 'header': 'Season', 'title': 'Fall'},
    {'year': 2027, 'month': 12, 'day': 21, 'header': 'Season', 'title': 'Winter'},

    # Seasons 2028:
    {'year': 2028, 'month': 3, 'day': 19, 'header': 'Season', 'title': 'Spring'},
    {'year': 2028, 'month': 6, 'day': 20, 'header': 'Season', 'title': 'Summer'},
    {'year': 2028, 'month': 9, 'day': 22, 'header': 'Season', 'title': 'Fall'},
    {'year': 2028, 'month': 12, 'day': 21, 'header': 'Season', 'title': 'Winter'},

    # Seasons 2029:
    {'year': 2029, 'month': 3, 'day': 20, 'header': 'Season', 'title': 'Spring'},
    {'year': 2029, 'month': 6, 'day': 20, 'header': 'Season', 'title': 'Summer'},
    {'year': 2029, 'month': 9, 'day': 22, 'header': 'Season', 'title': 'Fall'},
    {'year': 2029, 'month': 12, 'day': 21, 'header': 'Season', 'title': 'Winter'},

    # Seasons 2030:
    {'year': 2030, 'month': 3, 'day': 20, 'header': 'Season', 'title': 'Spring'},
    {'year': 2030, 'month': 6, 'day': 21, 'header': 'Season', 'title': 'Summer'},
    {'year': 2030, 'month': 9, 'day': 22, 'header': 'Season', 'title': 'Fall'},
    {'year': 2030, 'month': 12, 'day': 21, 'header': 'Season', 'title': 'Winter'},

    # Family Events
    {'month': 3, 'day': 17, 'header': 'Birthday', 'title': 'Corinne', 'msg': 'Happy Birthday, Corinne!', 'icon': 'birthday'},  # noqa: E501
    {'month': 6, 'day': 9, 'header': 'Birthday', 'title': 'Kyle', 'msg': 'Happy Birthday, Kyle!', 'icon': 'birthday'},
    {'month': 9, 'day': 20, 'header': 'Birthday', 'title': 'Jess', 'msg': 'Happy Birthday, Jess!', 'icon': 'birthday'},
    {'month': 10, 'day': 28, 'header': 'Birthday', 'title': 'Heather', 'msg': 'Happy Birthday, Heather!', 'icon': 'birthday'},  # noqa: E501
    {'month': 6, 'day': 23, 'header': 'Anniversary', 'title': 'Kyle & Jess', 'msg': 'Happy Anniversary!', 'icon': 'birthday'},  # noqa: E501

]


def _find_event_for_day(day):
    return next(
        (
            e for e in EVENTS if day.month == e['month']
            and day.day == e['day']
            and ('year' not in e or day.year == e['year'])
        ), None
    )


def fetch(today):
    # today = datetime.date(2018, 12, 25)
    plus_one = today + datetime.timedelta(days=1)
    plus_two = plus_one + datetime.timedelta(days=1)
    plus_three = plus_two + datetime.timedelta(days=1)
    return {
        'today': _find_event_for_day(today),
        'plus_one': _find_event_for_day(plus_one),
        'plus_two': _find_event_for_day(plus_two),
        'plus_three': _find_event_for_day(plus_three),
    }
