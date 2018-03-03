# Generate in image from the provided weather, calendar, special_events data
from PIL import Image, ImageDraw, ImageFont
from util import local_file

EPD_WIDTH = 640
EPD_HEIGHT = 384
BLACK = 0
WHITE = 255
RED = 128

COLUMN_WIDTH = 160
# TODO: Generate subroutines to fill in subsections by size, then composite those sections back together
#       Which should allow me to much more easily align things to edges and distribute whitespace

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

def _load_weather_icon(icon):
    return Image.open(local_file('icons/weather/' + WEATHER_ICON_MAP[icon])) # Expecting 64x64 monochrome icons

def _centered_text(draw, text, font, width, offset):
    dimensions = draw.textsize(text, font=font)
    return ((width - dimensions[0]) // 2 + offset[0], offset[1])

def _draw_forecast(image, draw, column_left, header, forecast, header_font, body_font):
    draw.text(_centered_text(draw, header, header_font, COLUMN_WIDTH, (column_left, 0)), header, font=header_font, fill=BLACK)
    msg = str(forecast['low-temperature']) + '–' + str(forecast['high-temperature']) # Center before adding the °
    draw.text(_centered_text(draw, msg, body_font, COLUMN_WIDTH, (column_left, 40)), msg  + '°', font=body_font, fill=BLACK)
    try:
        icon = _load_weather_icon(forecast['icon'])
        image.paste(icon, ((COLUMN_WIDTH - icon.size[0]) // 2 + column_left, 65))
    except:
        draw.text(_centered_text(draw, forecast['description'], body_font, COLUMN_WIDTH, (column_left, 65)), forecast['description'], font=body_font, fill=BLACK)

def create(weather, calendar, special_event):
    image = Image.new('L', (EPD_WIDTH, EPD_HEIGHT), WHITE)    # 255: clear the frame
    draw = ImageDraw.Draw(image)
    draw.fontmode = '1' # No Anti-aliasing
    header_font = ImageFont.truetype(local_file('fonts/FreeSansBold.ttf'), 36)
    body_font = ImageFont.truetype(local_file('fonts/FreeSans.ttf'), 24)
    detail_font = ImageFont.truetype(local_file('fonts/FreeSans.ttf'), 14)

    # Bottom-right corner
    dimensions = draw.textsize(weather['current']['time'], font=detail_font)
    timestamp_height = dimensions[1]
    draw.text((EPD_WIDTH-dimensions[0], EPD_HEIGHT-dimensions[1]), weather['current']['time'], font=detail_font, fill=BLACK)

    # 1st Column
    msg = 'Current'
    draw.text(_centered_text(draw, msg, header_font, COLUMN_WIDTH, (0, 0)), msg, font=header_font, fill=BLACK)
    msg = str(weather['current']['temperature']) # Center before adding the °
    draw.text(_centered_text(draw, msg, body_font, COLUMN_WIDTH, (0, 40)), msg + '°', font=body_font, fill=BLACK)
    try:
        icon = _load_weather_icon(weather['current']['icon'])
        image.paste(icon, ((COLUMN_WIDTH - icon.size[0]) // 2, 65))
    except:
        draw.text(_centered_text(draw, weather['current']['description'], body_font, COLUMN_WIDTH, (0, 65)), weather['current']['description'], font=body_font, fill=BLACK)

    # 2nd Column
    _draw_forecast(image, draw, COLUMN_WIDTH, 'Today', weather['forecast']['today'], header_font, body_font)

    # 3rd Column
    _draw_forecast(image, draw, COLUMN_WIDTH*2, weather['forecast']['tomorrow']['weekday'], weather['forecast']['tomorrow'], header_font, body_font)

    # 4th Column
    _draw_forecast(image, draw, COLUMN_WIDTH*3, weather['forecast']['day_after']['weekday'], weather['forecast']['day_after'], header_font, body_font)

    if (special_event):
        dimensions = draw.textsize(special_event['msg'], font=header_font)
        draw.text(((EPD_WIDTH - dimensions[0]) // 2, EPD_HEIGHT - dimensions[1] - timestamp_height), special_event['msg'], font=header_font, fill=RED)

    return image
