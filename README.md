# Home Board

A set of scripts to load "agenda" data and display it on a [Waveshare ePaper display (7.5 inch, 3 color)](https://www.waveshare.com/product/7.5inch-e-paper-hat-b.htm) -
Powered by a Raspberry Pi (in my case, a Raspberry Pi Model B Rev 2).

Written for Python3 (tested on 3.7), utilizes pipenv.

## Setup

1. Use an RPi image with desktop, we need a web browser to complete the OAuth2 Flow for Google.
2. After installing the RPi image, use the RPi config gui or `raspi-config` command to enable SPI (under "Interfaces").
3. Install python3.7 and libpython3.7-dev: `sudo apt install python3.7 libpython3.7-dev`.
4. Install/upgrade pip: `python3.7 -m pip install --user --upgrade pip`.
5. Install pipenv: `python3.7 -m pip install --user --upgrade pipenv`.
6. Install application dependencies via pipenv: `cd homeBoard && pipenv install`.
7. Configure Google Calendar and Weather by editing `home_board/calendar.py` and `home_board/nws.py`
8. Generate Oauth2 credentials: `pipenv run python -c "from home_board.calendar import generate_credentials; generate_credentials()"`.
    - Follow prompts in browser to complete authentication.
9. Run application: `pipenv run python main.py`

## Details

Pulls weather conditions and forecasting from the [National Weather Service](https://www.weather.gov/documentation/services-web-api) (NO API Key required).

Pulls Calendering information from [Google Calendar](https://developers.google.com/google-apps/calendar/) (OAuth2 authentication required).

After configuring weather and calendaring APIs:

Note: As far as I can tell, you need to generate the OAuth2 credentials on the device that will run homeBoard.  You can generate them elsewhere and then copy them to the device, but for me they wouldn't refresh as the device was unknown to Google.  Once I generated on the device they were able to automatically refresh.

Pulls Special Events from a locally-defined Dict.

Determines Daylight Saving Time changes from the defined timezone using pytz. (Can do this, currently disabled.)

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

Original icons from flaticons.net and then modified, except windy.bmp and cloudy_windy.bmp.
windy.bmp and cloudy_windy.bmp modified from https://www.flaticon.com/free-icon/wind_56086, original by Yannick.

Run DocTests:

    > pipenv run python doctest_runner.py -v

Example Crontab entries:

    > # Update every 15 minutes during the day
    > */15 7-21 * * * /home/pi/.local/share/virtualenvs/homeBoard--Ftpympu/bin/python3 /home/pi/homeBoard/main.py 2>&1 | /usr/bin/logger -t homeBoard
    > # Only update once per hour overnight
    > 0 22-23,0-6 * * * /home/pi/.local/share/virtualenvs/homeBoard--Ftpympu/bin/python3 /home/pi/homeBoard/main.py 2>&1 | /usr/bin/logger -t homeBoard

Example Crontab entries using Flock to avoid simultaneous executions (which usually result in image corruption on the display):

    > # Update every 15 minutes during the day
    > */15 7-21 * * * /usr/bin/flock -n /home/pi/homeBoard_cron.lock -c "/home/pi/.local/share/virtualenvs/homeBoard--Ftpympu/bin/python3 /home/pi/homeBoard/main.py 2>&1 | /usr/bin/logger -t homeBoard"
    > # Only update once per hour overnight
    > 0 22-23,0-6 * * * /usr/bin/flock -n /home/pi/homeBoard_cron.lock -c "/home/pi/.local/share/virtualenvs/homeBoard--Ftpympu/bin/python3 /home/pi/homeBoard/main.py 2>&1 | /usr/bin/logger -t homeBoard"
