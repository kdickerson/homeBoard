# Fetch weather info from National Weather Service
import datetime
import json
import logging
import re
from urllib.request import Request, urlopen

from .util import local_file

CONDITIONS_STATION_ID = 'KLVK'  # NWS Station ID to get latest observation
FORECAST_COORDINATES = '37.690835,-121.786962'  # GPS Coordinates for which to get the forecast; No space between
CONDITIONS_URL = 'https://api.weather.gov/stations/{station_id}/observations/latest?require_qc=false'
FORECAST_URL = 'https://api.weather.gov/points/{coordinates}/forecast'
MOCK_NWS_DATA = False
MOCK_NWS_CONDITIONS_DATA_FILE = 'mock_data/mock_nws_conditions_data.json'
MOCK_NWS_FORECAST_DATA_FILE = 'mock_data/mock_nws_forecast_data.json'
# Example icon URL: https://api.weather.gov/icons/land/day/sct?size=medium - we want "sct"
ICON_EXTRACTOR_REGEX = 'https://api.weather.gov/icons/land/(?:day|night)/(\\w+).*'
ICON_EXTRACTOR = re.compile(ICON_EXTRACTOR_REGEX)

# List of NWS Icons found at https://api.weather.gov/icons
# Map NWS Icon values to match the strings expected by Compositor
ICON_MAP = {
    'bkn': 'mostlycloudy',
    'blizzard': 'snow',
    'cold': 'clear',
    'dust': 'hazy',
    'few': 'clear',
    'fog': 'fog',
    'fzra': 'sleet',
    'haze': 'hazy',
    'hot': 'sunny',
    'hurricane': 'rain',
    'ovc': 'mostlycloudy',
    'rain_fzra': 'sleet',
    'rain_showers_hi': 'rain',
    'rain_showers': 'rain',
    'rain_sleet': 'sleet',
    'rain_snow': 'snow',
    'rain': 'rain',
    'sct': 'partlycloudy',
    'skc': 'clear',
    'sleet': 'sleet',
    'smoke': 'hazy',
    'snow_fzra': 'sleet',
    'snow_sleet': 'sleet',
    'snow': 'snow',
    'tornado': 'tstorms',
    'tropical_storm': 'rain',
    'tsra_hi': 'tstorms',
    'tsra_sct': 'tstorms',
    'tsra': 'tstorms',
    'wind_bkn': 'cloudy_windy',
    'wind_few': 'windy',
    'wind_ovc': 'cloudy_windy',
    'wind_sct': 'cloudy_windy',
    'wind_skc': 'windy',
}


def _celsius_to_fahrenheit(degrees):
    return round((degrees * 9/5) + 32)


def _coalesce_forecasts(forecasts):
    '''
        NWS returns forecasts in half-day increments.
        This coalesces those increments into whole-day values that the rest of the code expects.
    '''
    by_date = {}
    for forecast in forecasts:
        if forecast['name'] == 'Tonight':
            # Need to populate tonight as the first entry in our coalesced forecasts, otherwise the forecast
            # displayed jumps to tomorrow's and it's off by a day until midnight.
            time_string = forecast['startTime']  # 2019-02-16T18:00:00-08:00
            if ":" == time_string[-3:-2]:  # Remove the colon from the timezone data
                time_string = time_string[:-3] + time_string[-2:]
            startTime = datetime.datetime.strptime(time_string, '%Y-%m-%dT%H:%M:%S%z')  # 2019-02-16T18:00:00-0800
            by_date[startTime.date()] = {
                'date': startTime.date(),
                'high': forecast['temperature'],
                'low': forecast['temperature'],
                'description': forecast['shortForecast'],
                'icon': forecast['icon'],
            }

        time_string = forecast['endTime']  # 2019-02-16T18:00:00-08:00
        if ":" == time_string[-3:-2]:  # Remove the colon from the timezone data
            time_string = time_string[:-3] + time_string[-2:]
        endTime = datetime.datetime.strptime(time_string, '%Y-%m-%dT%H:%M:%S%z')  # 2019-02-16T18:00:00-0800

        if endTime.date() not in by_date:
            by_date[endTime.date()] = {'date': None, 'high': '-', 'low': '-', 'description': None, 'icon': None}

        if endTime.time().hour >= 12:
            by_date[endTime.date()]['date'] = endTime.date()
            by_date[endTime.date()]['high'] = forecast['temperature']
            by_date[endTime.date()]['description'] = forecast['shortForecast']
            by_date[endTime.date()]['icon'] = forecast['icon']
        else:
            by_date[endTime.date()]['date'] = endTime.date()  # Always set date. Ensure we have it for half increments
            by_date[endTime.date()]['low'] = forecast['temperature']  # The low from the night leading into this date

    coalesced_forecasts = sorted(by_date.values(), key=lambda forecast: forecast['date'])
    logging.debug('Coalesced Forecasts:' + str(coalesced_forecasts))
    return coalesced_forecasts


def _request_data(station_id, coordinates):
    logging.debug('_request_data:start')
    if MOCK_NWS_DATA:
        with open(local_file(MOCK_NWS_CONDITIONS_DATA_FILE)) as mock_data:
            conditions_json_string = mock_data.read()
        with open(local_file(MOCK_NWS_FORECAST_DATA_FILE)) as mock_data:
            forecast_json_string = mock_data.read()
    else:
        conditions_url = CONDITIONS_URL.format(station_id=station_id)
        logging.debug("NWS Conditions URL: " + conditions_url)
        conditions_request = Request(conditions_url, headers={
            'User-Agent': 'https://github.com/kdickerson/homeBoard',
            'Accept': 'application/geo+json',
        })
        with urlopen(conditions_request, timeout=60) as response:
            conditions_json_string = response.read().decode('utf8')

        forecast_url = FORECAST_URL.format(coordinates=coordinates)
        logging.debug("NWS Forecast URL: " + forecast_url)
        forecast_request = Request(forecast_url, headers={
            'User-Agent': 'https://github.com/kdickerson/homeBoard',
            'Accept': 'application/geo+json',
        })
        with urlopen(forecast_request, timeout=60) as response:
            forecast_json_string = response.read().decode('utf8')

    conditions_parsed_json = json.loads(conditions_json_string)
    forecast_parsed_json = json.loads(forecast_json_string)
    forecasts = _coalesce_forecasts(forecast_parsed_json['properties']['periods'])
    logging.debug('_request_data:end')
    return conditions_parsed_json['properties'], forecasts


def _extract_cleaned_forecast(day_idx, forecasts):
    return {
        'low-temperature': forecasts[day_idx]['low'],
        'high-temperature': forecasts[day_idx]['high'],
        'description': forecasts[day_idx]['description'],
        'icon': _normalize_icon(_extract_icon(forecasts[day_idx]['icon'])),
        'date': forecasts[day_idx]['date'],
    }


def _extract_icon(raw_icon):
    icon = None
    icon_match = ICON_EXTRACTOR.match(raw_icon)
    if icon_match:
        icon = icon_match.group(1)
    return icon


def _normalize_icon(nws_icon):
    return ICON_MAP[nws_icon] if nws_icon is not None else 'unknown'


def _nws_data():
    logging.debug('_nws_data:start')
    current, forecasts = _request_data(CONDITIONS_STATION_ID, FORECAST_COORDINATES)

    cleaned_current = {
        'temperature': _celsius_to_fahrenheit(current['temperature']['value']),
        'description': current['textDescription'],
        'icon': _normalize_icon(_extract_icon(current['icon'])),
    }

    cleaned_forecast = {
        'today': _extract_cleaned_forecast(0, forecasts),
        'plus_one': _extract_cleaned_forecast(1, forecasts),
        'plus_two': _extract_cleaned_forecast(2, forecasts),
        'plus_three': _extract_cleaned_forecast(3, forecasts),
    }
    logging.debug('_nws_data:end')
    return cleaned_current, cleaned_forecast


def fetch():
    current, forecast = _nws_data()
    return {
        'current': current,
        'forecast': forecast
    }
