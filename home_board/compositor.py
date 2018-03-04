# Generate in image from the provided weather, calendar, special_events data
from PIL import Image, ImageDraw, ImageFont
from .util import local_file
import os

EPD_WIDTH = 640
EPD_HEIGHT = 384
BLACK = 0
WHITE = 255
RED = 128

COLUMN_WIDTH = 160
CALENDAR_TOP = 130
CALENDAR_BOTTOM = 305

WEATHER_ICON_MAP = {
    'chanceflurries': 'chancesnow.bmp',
    'chancerain': 'chancerain.bmp',
    'chancesleet': 'chancesnow.bmp',
    'chancesnow': 'chancesnow.bmp',
    'chancetstorms': 'chancetstorms.bmp',
    'clear': 'sunny.bmp',
    'cloudy': 'cloudy.bmp',
    'flurries': 'snow.bmp',
    'fog': 'fog.bmp',
    'hazy': 'hazy.bmp',
    'mostlycloudy': 'mostlycloudy.bmp',
    'partlycloudy': 'partlycloudy.bmp',
    'partlysunny': 'mostlycloudy.bmp',
    'sleet': 'snow.bmp',
    'rain': 'rain.bmp',
    'snow': 'snow.bmp',
    'sunny': 'sunny.bmp',
    'tstorms': 'tstorms.bmp',
    'unknown': 'sunny.bmp',
}

EVENT_ICON_MAP = {
    'birthday': 'birthday.bmp',
    'christmas': 'christmas.bmp',
    'halloween': 'halloween.bmp',
}

WEATHER_ICON_PATH = '../icons/weather/'
EVENTS_ICON_PATH = '../icons/events/'

def _load_weather_icon(icon):
    return Image.open(local_file(os.path.join(WEATHER_ICON_PATH, WEATHER_ICON_MAP[icon]))) # Expecting 64x64 monochrome icons

def _load_event_icon(icon):
    return Image.open(local_file(os.path.join(EVENTS_ICON_PATH, EVENT_ICON_MAP[icon])))

def _centered_text(draw, text, font, width, offset):
    dimensions = draw.textsize(text, font=font)
    return ((width - dimensions[0]) // 2 + offset[0], offset[1])

def _truncate_text(draw, text, font, width):
    dimensions = draw.textsize(text, font=font)
    i = 0
    while dimensions[0] > width:
        i = i - 1
        dimensions = draw.textsize(text[:i], font=font)
    return (text[:i-1] + '…') if i < 0 else text, dimensions

def _calendar_draw_day(image, draw, events, offset, time_font, description_font):
    padding = 10
    top = offset[1]
    for event in events:
        header = ('' if event['all_day'] else event['start'].strftime('%-H:%M') + ' ') + event['calendar_label'] # %-H is Linux specific
        time, time_dim = _truncate_text(draw, header, time_font, COLUMN_WIDTH - padding)
        desc, desc_dim = _truncate_text(draw, event['description'], description_font, COLUMN_WIDTH - padding - padding) # 2nd padding for left-margin
        if top + time_dim[1] + desc_dim[1] > CALENDAR_BOTTOM:
            break
        draw.text((offset[0], top), time, font=time_font, fill=BLACK)
        draw.text((offset[0] + padding, top + time_dim[1]), desc, font=description_font, fill=BLACK)
        top = top + time_dim[1] + desc_dim[1] + padding

def _weather_draw_today(image, draw, conditions, forecast, header_font, temp_font):
    draw.text(_centered_text(draw, 'Today', header_font, COLUMN_WIDTH, (0, 0)), 'Today', font=header_font, fill=BLACK)
    SUB_COLUMN_WIDTH = COLUMN_WIDTH // 2

    # Sub column 1:
    cur_size = draw.textsize(str(conditions['temperature']), font=temp_font)
    draw.text(_centered_text(draw, str(conditions['temperature']), temp_font, SUB_COLUMN_WIDTH, (0, 40)), str(conditions['temperature']) + '°', font=temp_font, fill=BLACK)

    # Sub column 2:
    forecast_msg = str(forecast['high-temperature'])
    forecast_size = draw.textsize(forecast_msg, font=temp_font)
    detail_offset = cur_size[1] - forecast_size[1]
    draw.text(_centered_text(draw, forecast_msg, temp_font, SUB_COLUMN_WIDTH, (SUB_COLUMN_WIDTH, 40 + detail_offset)), forecast_msg + '°', font=temp_font, fill=BLACK)

    try:
        cur_icon = _load_weather_icon(conditions['icon'])
        forecast_icon = _load_weather_icon(forecast['icon'])
        image.paste(cur_icon, ((SUB_COLUMN_WIDTH - cur_icon.size[0]) // 2, 65))
        image.paste(forecast_icon, ((SUB_COLUMN_WIDTH - cur_icon.size[0]) // 2 + SUB_COLUMN_WIDTH, 65))
    except:
        draw.text(_centered_text(draw, conditions['description'], temp_font, COLUMN_WIDTH, (0, 65)), conditions['description'], font=temp_font, fill=BLACK)

    separator = '⇝'
    draw.text(_centered_text(draw, separator, temp_font, COLUMN_WIDTH, (0, 55)), separator, font=temp_font, fill=BLACK)

def _weather_draw_forecast(image, draw, column_left, header, forecast, header_font, temp_font):
    draw.text(_centered_text(draw, header, header_font, COLUMN_WIDTH, (column_left, 0)), header, font=header_font, fill=BLACK)
    msg = str(forecast['low-temperature']) + '–' + str(forecast['high-temperature']) # Center before adding the °
    draw.text(_centered_text(draw, msg, temp_font, COLUMN_WIDTH, (column_left, 40)), msg + '°', font=temp_font, fill=BLACK)
    try:
        icon = _load_weather_icon(forecast['icon'])
        image.paste(icon, ((COLUMN_WIDTH - icon.size[0]) // 2 + column_left, 65))
    except:
        draw.text(_centered_text(draw, forecast['description'], temp_font, COLUMN_WIDTH, (column_left, 65)), forecast['description'], font=temp_font, fill=BLACK)

def _special_event_draw(image, draw, event, offset_bottom, font):
    textsize = draw.textsize(event['msg'], font=font)
    iconsize = [0, 0]
    icon = None
    try:
        icon = _load_event_icon(event['icon']) if event['icon'] else None
        if icon:
            iconsize = icon.size
    except:
        raise

    if icon:
        padding = 5
        msgsize = (iconsize[0] + textsize[0] + padding, max(textsize[1], iconsize[1]))
    else:
        padding = 0
        msgsize = textsize

    left = (EPD_WIDTH - msgsize[0]) // 2
    top = EPD_HEIGHT - msgsize[1] - offset_bottom
    image.paste(icon, (left, top + (msgsize[1] - iconsize[1]) // 2)) if icon else None
    draw.text((left + iconsize[0] + padding, top + (msgsize[1] - textsize[1]) // 2), event['msg'], font=font, fill=RED)

def create(weather, calendar, special_event):
    image = Image.new('L', (EPD_WIDTH, EPD_HEIGHT), WHITE)    # 255: clear the frame
    draw = ImageDraw.Draw(image)
    draw.fontmode = '1' # No Anti-aliasing
    header_font = ImageFont.truetype(local_file('fonts/FreeSansBold.ttf'), 36)
    special_font = header_font
    temp_font = ImageFont.truetype(local_file('fonts/FreeSans.ttf'), 24)
    cal_time_font = ImageFont.truetype(local_file('fonts/FreeSans.ttf'), 20)
    cal_text_font = ImageFont.truetype(local_file('fonts/FreeSans.ttf'), 16)
    footer_font = ImageFont.truetype(local_file('fonts/FreeSans.ttf'), 14)

    # Footer: Bottom-right corner
    if weather:
        dimensions = draw.textsize(weather['current']['time'], font=footer_font)
        timestamp_height = dimensions[1]
        draw.text((EPD_WIDTH-dimensions[0], EPD_HEIGHT-dimensions[1]), weather['current']['time'], font=footer_font, fill=BLACK)

    # 1st Column
    if weather: _weather_draw_today(image, draw, weather['current'], weather['forecast']['today'], header_font, temp_font)
    if calendar: _calendar_draw_day(image, draw, calendar['today'], (0, CALENDAR_TOP), cal_time_font, cal_text_font)

    # 2nd Column
    if weather: _weather_draw_forecast(image, draw, COLUMN_WIDTH, weather['forecast']['plus_one']['weekday'], weather['forecast']['plus_one'], header_font, temp_font)
    if calendar: _calendar_draw_day(image, draw, calendar['plus_one'], (COLUMN_WIDTH, CALENDAR_TOP), cal_time_font, cal_text_font)

    # 3rd Column
    if weather: _weather_draw_forecast(image, draw, COLUMN_WIDTH*2, weather['forecast']['plus_two']['weekday'], weather['forecast']['plus_two'], header_font, temp_font)
    if calendar: _calendar_draw_day(image, draw, calendar['plus_two'], (COLUMN_WIDTH*2, CALENDAR_TOP), cal_time_font, cal_text_font)

    # 4th Column
    if weather: _weather_draw_forecast(image, draw, COLUMN_WIDTH*3, weather['forecast']['plus_three']['weekday'], weather['forecast']['plus_three'], header_font, temp_font)
    if calendar: _calendar_draw_day(image, draw, calendar['plus_three'], (COLUMN_WIDTH*3, CALENDAR_TOP), cal_time_font, cal_text_font)

    if special_event:
        _special_event_draw(image, draw, special_event, timestamp_height, special_font)

    return image
