# Fetch special event info (Birthdays, Holidays, Anniversaries, etc. with image)
import datetime

EVENTS = [
    {'month': 3, 'day': 17, 'msg': 'Happy Birthday, Corinne!', 'icon': 'birthday'}
]

def fetch():
    now = datetime.datetime.now()
    return next((e for e in EVENTS if now.month == e['month'] and now.day == e['day']), None)
