# Fetch special event info (Birthdays, Holidays, Anniversaries, etc. with image)
import datetime

EVENTS = [
    {'month': 3, 'day': 17, 'msg': 'Happy Birthday, Corinne!', 'icon': 'birthday'},
    {'month': 6, 'day': 9, 'msg': 'Happy Birthday, Kyle!', 'icon': 'birthday'},
    {'month': 9, 'day': 20, 'msg': 'Happy Birthday, Jess!', 'icon': 'birthday'},
    {'month': 10, 'day': 28, 'msg': 'Happy Birthday, Heather!', 'icon': 'birthday'},
    {'month': 10, 'day': 31, 'msg': 'Happy Halloween!', 'icon': 'halloween'},
    {'month': 12, 'day': 25, 'msg': 'Merry Christmas!', 'icon': 'christmas'},
]

def fetch():
    now = datetime.date.now()
    #now = datetime.date(2018, 12, 25)
    return next((e for e in EVENTS if now.month == e['month'] and now.day == e['day']), None)
