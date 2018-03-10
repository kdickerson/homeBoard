# Fetch weather info from WUnderground and/or local station, process, and return
from urllib.request import urlopen
import json
from .util import local_file

CLIENT_SECRET_FILE = 'private/wunderground.key'
PWS_ID = 'KCALIVER107' # Wunderground Personal Weather Station ID
MOCK_WUNDERGROUND_DATA = False
MOCK_WUNDERGROUND_DATA_FILE = 'mock_data/mock_wunderground_data.json'

def _request_data(api_key, pws_id):
    if MOCK_WUNDERGROUND_DATA:
        with open(local_file(MOCK_WUNDERGROUND_DATA_FILE)) as mock_data:
            json_string = mock_data.read()
    else:
        query_url = 'http://api.wunderground.com/api/{api_key}/conditions/forecast/q/pws:{pws_id}.json'.format(api_key=api_key, pws_id=pws_id)
        with urlopen(query_url) as response:
            json_string = response.read().decode('utf8')
    parsed_json = json.loads(json_string)
    return parsed_json['current_observation'], parsed_json['forecast']['simpleforecast']['forecastday']

def _extract_cleaned_forecast(day_idx, forecasts):
    return {
        'low-temperature': forecasts[day_idx]['low']['fahrenheit'],
        'high-temperature': forecasts[day_idx]['high']['fahrenheit'],
        'description': forecasts[day_idx]['conditions'],
        'icon': forecasts[day_idx]['icon'],
    }

def _wunderground_data():
    with open(local_file(CLIENT_SECRET_FILE)) as key_file:
        api_key = key_file.read().strip()

    current, forecasts = _request_data(api_key, PWS_ID)
    cleaned_current = {
        'time': current['observation_time'],
        'temperature': current['temp_f'],
        'wind': current['wind_mph'],
        'description': current['weather'],
        'icon': current['icon']
    }
    cleaned_forecast = {
        'today': _extract_cleaned_forecast(0, forecasts),
        'plus_one': _extract_cleaned_forecast(1, forecasts),
        'plus_two': _extract_cleaned_forecast(2, forecasts),
        'plus_three': _extract_cleaned_forecast(3, forecasts),
    }
    return cleaned_current, cleaned_forecast

def fetch():
    current, forecast = _wunderground_data()
    return {
        'current': current,
        'forecast': forecast
    }
