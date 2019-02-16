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
    {'year': 2019, 'month': 11, 'day': 28, 'msg': 'Happy Thanksgiving!', 'icon': 'thanksgiving'},
    {'year': 2020, 'month': 11, 'day': 26, 'msg': 'Happy Thanksgiving!', 'icon': 'thanksgiving'},
    {'year': 2021, 'month': 11, 'day': 25, 'msg': 'Happy Thanksgiving!', 'icon': 'thanksgiving'},
    {'year': 2022, 'month': 11, 'day': 24, 'msg': 'Happy Thanksgiving!', 'icon': 'thanksgiving'},
    {'year': 2023, 'month': 11, 'day': 23, 'msg': 'Happy Thanksgiving!', 'icon': 'thanksgiving'},
    {'year': 2024, 'month': 11, 'day': 28, 'msg': 'Happy Thanksgiving!', 'icon': 'thanksgiving'},
    {'year': 2025, 'month': 11, 'day': 27, 'msg': 'Happy Thanksgiving!', 'icon': 'thanksgiving'},
    # Seasons 2019:
    {'year': 2019, 'month': 3, 'day': 20, 'header': 'Season', 'title': 'Spring'},
    {'year': 2019, 'month': 6, 'day': 21, 'header': 'Season', 'title': 'Summer'},
    {'year': 2019, 'month': 9, 'day': 23, 'header': 'Season', 'title': 'Fall'},
    {'year': 2019, 'month': 12, 'day': 21, 'header': 'Season', 'title': 'Winter'},
    # Seasons 2020:
    {'year': 2020, 'month': 3, 'day': 19, 'header': 'Season', 'title': 'Spring'},
    {'year': 2020, 'month': 6, 'day': 21, 'header': 'Season', 'title': 'Summer'},
    {'year': 2020, 'month': 9, 'day': 23, 'header': 'Season', 'title': 'Fall'},
    {'year': 2020, 'month': 12, 'day': 21, 'header': 'Season', 'title': 'Winter'},
    # Seasons 2021:
    {'year': 2021, 'month': 3, 'day': 20, 'header': 'Season', 'title': 'Spring'},
    {'year': 2021, 'month': 6, 'day': 20, 'header': 'Season', 'title': 'Summer'},
    {'year': 2021, 'month': 9, 'day': 22, 'header': 'Season', 'title': 'Fall'},
    {'year': 2021, 'month': 12, 'day': 21, 'header': 'Season', 'title': 'Winter'},
    # Seasons 2022:
    {'year': 2022, 'month': 3, 'day': 20, 'header': 'Season', 'title': 'Spring'},
    {'year': 2022, 'month': 6, 'day': 21, 'header': 'Season', 'title': 'Summer'},
    {'year': 2022, 'month': 9, 'day': 22, 'header': 'Season', 'title': 'Fall'},
    {'year': 2022, 'month': 12, 'day': 21, 'header': 'Season', 'title': 'Winter'},
    # Seasons 2023:
    {'year': 2023, 'month': 3, 'day': 20, 'header': 'Season', 'title': 'Spring'},
    {'year': 2023, 'month': 6, 'day': 21, 'header': 'Season', 'title': 'Summer'},
    {'year': 2023, 'month': 9, 'day': 22, 'header': 'Season', 'title': 'Fall'},
    {'year': 2023, 'month': 12, 'day': 21, 'header': 'Season', 'title': 'Winter'},
    # Seasons 2024:
    {'year': 2024, 'month': 3, 'day': 19, 'header': 'Season', 'title': 'Spring'},
    {'year': 2024, 'month': 6, 'day': 20, 'header': 'Season', 'title': 'Summer'},
    {'year': 2024, 'month': 9, 'day': 22, 'header': 'Season', 'title': 'Fall'},
    {'year': 2024, 'month': 12, 'day': 21, 'header': 'Season', 'title': 'Winter'},
    # Seasons 2025:
    {'year': 2025, 'month': 3, 'day': 20, 'header': 'Season', 'title': 'Spring'},
    {'year': 2025, 'month': 6, 'day': 20, 'header': 'Season', 'title': 'Summer'},
    {'year': 2025, 'month': 9, 'day': 22, 'header': 'Season', 'title': 'Fall'},
    {'year': 2025, 'month': 12, 'day': 21, 'header': 'Season', 'title': 'Winter'},

    # Family Events
    {'month': 3, 'day': 17, 'header': 'Birthday', 'title': 'Corinne', 'msg': 'Happy Birthday, Corinne!', 'icon': 'birthday'},
    {'month': 6, 'day': 9, 'header': 'Birthday', 'title': 'Kyle', 'msg': 'Happy Birthday, Kyle!', 'icon': 'birthday'},
    {'month': 9, 'day': 20, 'header': 'Birthday', 'title': 'Jess', 'msg': 'Happy Birthday, Jess!', 'icon': 'birthday'},
    {'month': 10, 'day': 28, 'header': 'Birthday', 'title': 'Heather', 'msg': 'Happy Birthday, Heather!', 'icon': 'birthday'},
    {'month': 6, 'day': 23, 'header': 'Anniversary', 'title': 'Kyle & Jess', 'msg': 'Happy Anniversary!', 'icon': 'birthday'},

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
