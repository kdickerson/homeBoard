# Fetch weather info from WUnderground and/or local station, process, and return
from urllib.request import urlopen
import json
import os

PWS_ID = 'KCALIVER107' # Wunderground Personal Weather Station ID
MOCK_WUNDERGROUND_DATA = False

def _request_data(api_key, pws_id):
    if MOCK_WUNDERGROUND_DATA:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mock_wunderground_data.json')) as mock_data:
            json_string = mock_data.read()
    else:
        query_url = 'http://api.wunderground.com/api/{api_key}/conditions/forecast/q/pws:{pws_id}.json'.format(api_key=api_key, pws_id=pws_id)
        with urlopen(query_url) as response:
            json_string = response.read().decode('utf8')
    parsed_json = json.loads(json_string)
    return parsed_json['current_observation'], parsed_json['forecast']['simpleforecast']['forecastday']

def _wunderground_data():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wunderground.key')) as key_file:
        api_key = key_file.read().strip()

    current, forecasts = _request_data(api_key, PWS_ID)
    cleaned_current = {
        'time': current['observation_time'],
        'temperature': current['temp_f'],
        'wind': current['wind_mph'],
        'description': current['weather'],
        'icon': None # TODO
    }
    cleaned_forecast = {
        'today': {
            'low-temperature': forecasts[0]['low']['fahrenheit'],
            'high-temperature': forecasts[0]['high']['fahrenheit'],
            'description': forecasts[0]['conditions'],
            'icon': None # TODO
        },
        'tomorrow': {
            'low-temperature': forecasts[1]['low']['fahrenheit'],
            'high-temperature': forecasts[1]['high']['fahrenheit'],
            'description': forecasts[1]['conditions'],
            'icon': None # TODO
        }
    }
    return cleaned_current, cleaned_forecast

def fetch(when):
    current, forecast = _wunderground_data()
    return {
        'current': current,
        'forecast': forecast
    }
