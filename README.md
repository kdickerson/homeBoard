# Home Board

A set of scripts to compile "agenda" data and display it on a Waveshare ePaper display (7.5 inch, 3 color) - Powered by a Raspberry Pi.

Written for Python3, utilizes pipenv.

Pulls weather conditions and forecasting from [Weather Underground (API Key required)](https://www.wunderground.com/weather/api/).

Pulls Calendering information from [Google Calendar](https://developers.google.com/google-apps/calendar/) (OAuth2 authentication required).

Note: As far as I can tell, you need to generate the OAuth2 credentials on the device that will run homeBoard.  You can generate them elsewhere and then copy them to the device, but for me they wouldn't refresh as the device was unknown to Google.  Once I generated on the device they were able to automatically refresh.

Pulls Special Events from a locally-defined Map.

Original icons from flaticons.net and then modified.
