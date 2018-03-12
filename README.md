# Home Board

A set of scripts to load "agenda" data and display it on a [Waveshare ePaper display (7.5 inch, 3 color)](https://www.waveshare.com/product/7.5inch-e-paper-hat-b.htm) - Powered by a Raspberry Pi.

Written for Python3 (tested on 3.5), utilizes pipenv.

Pulls weather conditions and forecasting from [Weather Underground](https://www.wunderground.com/weather/api/) (API Key required).

Pulls Calendering information from [Google Calendar](https://developers.google.com/google-apps/calendar/) (OAuth2 authentication required).

After configuring weather and calendaring APIs:

    > pipenv install
    > pipenv run python main

Note: As far as I can tell, you need to generate the OAuth2 credentials on the device that will run homeBoard.  You can generate them elsewhere and then copy them to the device, but for me they wouldn't refresh as the device was unknown to Google.  Once I generated on the device they were able to automatically refresh.

Pulls Special Events from a locally-defined Dict.

Determines Daylight Saving Time changes from the defined timezone using pytz.

Has functionality for using mock data at 2 levels:
 - High-level responses from data modules (useful for mocking specific displays)
  - Uses Pickle files due to JSON-incompatible data types
 - Low-level responses from remote APIs (useful for testing parsing changes without hitting API limits)
  - Uses JSON files

Can save a file, rather than send it to the display by passing "save" as the only parameter to main.py:

    > pipenv run python main.py save

Saved files are in grayscale with 3 possible values per pixel: 0, 128, and 255.  The display will interpret these values as Black, Red, and White, respectively.

The provided example images have been colorized to give a better idea of the end result.

Current weather conditions are displayed in red.
Calendar events that are currently happening are displayed in red.
Special Event messages are displayed in red.

Original icons from flaticons.net and then modified.
