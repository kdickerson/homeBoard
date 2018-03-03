# Fetch special event info (Birthdays, Holidays, Anniversaries, etc. with image)
import datetime

EVENTS = [
    {'month': 3, 'day': 17, 'msg': 'Happy Birthday, Corinne!', 'icon': 'birthday'}
]

def fetch(when):
    return next((e for e in EVENTS if when.month == e['month'] and when.day == e['day']), None)
