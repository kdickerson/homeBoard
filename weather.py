# Fetch weather info from WUnderground and/or local station, process, and return
import datetime

def fetch(when):
    return {
        'current': {
            'temperature': 55,
            'rain': 0.1,
            'wind': 0
        },
        'forecast': {
            'today': {
                'low-temperature': 37,
                'high-temperature': 58,
                'rain': 0,
                'wind': 0
            },
            'tomorrow': {
                'low-temperature': 45,
                'high-temperature': 60,
                'rain': 1,
                'wind': 5
            }
        }
    }
