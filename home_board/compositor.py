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
    'thanksgiving': 'thanksgiving.bmp'
}

WEATHER_ICON_PATH = 'icons/weather/'
EVENTS_ICON_PATH = 'icons/events/'
BLACK_TO_RED_LUT = [RED] + ([BLACK] * 254) + [WHITE] # Map BLACK to RED, leave WHITE alone; use with Image.point()

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

def _draw_header(draw, offset, text, font, color=BLACK):
    draw.text(_centered_text(draw, text, font, COLUMN_WIDTH, offset), text, font=font, fill=color)

def _draw_calendar(image, draw, events, offset, bottom, time_font, description_font):
    time_left_margin = 5
    text_left_margin = 5
    right_margin = 5
    bottom_margin = 5
    top = offset[1]
    more_msg_height = draw.textsize('+123456789 More', font=description_font)[1] # Max height for "+X More" msg
    for idx, event in enumerate(events):
        header = ('' if event['all_day'] else event['start'].strftime('%-H:%M') + ' ') + event['calendar_label'] # %-H is Linux specific
        time, time_dim = _truncate_text(draw, header, time_font, COLUMN_WIDTH - right_margin - time_left_margin)
        desc, desc_dim = _truncate_text(draw, event['description'], description_font, COLUMN_WIDTH - right_margin - text_left_margin)

        if top + time_dim[1] + desc_dim[1] + (0 if idx+1 is len(events) else more_msg_height) > bottom:
            more_msg = '+' + str(len(events) - idx) + ' More'
            draw.text(_centered_text(draw, more_msg, description_font, COLUMN_WIDTH, (offset[0], top)), more_msg, font=description_font, fill=BLACK)
            break
        draw.text((offset[0] + time_left_margin, top), time, font=time_font, fill=RED if event['underway'] else BLACK)
        draw.text((offset[0] + text_left_margin, top + time_dim[1]), desc, font=description_font, fill=RED if event['underway'] else BLACK)
        top = top + time_dim[1] + desc_dim[1] + bottom_margin

def _draw_forecast_and_current(image, draw, conditions, forecast, header_font, temp_font):
    SUB_COLUMN_WIDTH = COLUMN_WIDTH // 2

    # Sub column 1:
    cur_size = draw.textsize(str(conditions['temperature']), font=temp_font)
    draw.text(_centered_text(draw, str(conditions['temperature']), temp_font, SUB_COLUMN_WIDTH, (0, 40)), str(conditions['temperature']) + '°', font=temp_font, fill=RED)

    # Sub column 2:
    forecast_msg = str(forecast['high-temperature'])
    forecast_size = draw.textsize(forecast_msg, font=temp_font)
    detail_offset = cur_size[1] - forecast_size[1]
    draw.text(_centered_text(draw, forecast_msg, temp_font, SUB_COLUMN_WIDTH, (SUB_COLUMN_WIDTH, 40 + detail_offset)), forecast_msg + '°', font=temp_font, fill=BLACK)

    try:
        cur_icon = _load_weather_icon(conditions['icon']).point(BLACK_TO_RED_LUT)
        forecast_icon = _load_weather_icon(forecast['icon'])
        image.paste(cur_icon, ((SUB_COLUMN_WIDTH - cur_icon.size[0]) // 2, 65))
        image.paste(forecast_icon, ((SUB_COLUMN_WIDTH - cur_icon.size[0]) // 2 + SUB_COLUMN_WIDTH, 65))
    except:
        draw.text(_centered_text(draw, conditions['description'], temp_font, COLUMN_WIDTH, (0, 65)), conditions['description'], font=temp_font, fill=BLACK)

def _draw_forecast(image, draw, column_left, forecast, header_font, temp_font):
    msg = str(forecast['low-temperature']) + '–' + str(forecast['high-temperature']) # Center before adding the °
    draw.text(_centered_text(draw, msg, temp_font, COLUMN_WIDTH, (column_left, 40)), msg + '°', font=temp_font, fill=BLACK)
    try:
        icon = _load_weather_icon(forecast['icon'])
        image.paste(icon, ((COLUMN_WIDTH - icon.size[0]) // 2 + column_left, 65))
    except:
        draw.text(_centered_text(draw, forecast['description'], temp_font, COLUMN_WIDTH, (column_left, 65)), forecast['description'], font=temp_font, fill=BLACK)

def _draw_special_event(image, draw, event, footer_offset, font):
    textsize = draw.textsize(event['msg'], font=font)
    iconsize = (0, 0)
    icon = None
    try:
        icon = _load_event_icon(event['icon']) if 'icon' in event else None
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

    icon_left = (EPD_WIDTH - msgsize[0]) // 2
    icon_top = footer_offset[1] - msgsize[1]
    icon_offset = (icon_left, icon_top + (msgsize[1] - iconsize[1]) // 2)
    text_offset = (icon_left + iconsize[0] + padding, icon_top + (msgsize[1] - textsize[1]) // 2)
    text_to_footer_gap = footer_offset[1] - (text_offset[1] + textsize[1])
    if text_to_footer_gap > 0:
        icon_offset = (icon_offset[0], icon_offset[1] + text_to_footer_gap)
        text_offset = (text_offset[0], text_offset[1] + text_to_footer_gap)
    image.paste(icon, icon_offset) if icon else None
    draw.text(text_offset, event['msg'], font=font, fill=RED)
    return (min(icon_offset[0], text_offset[0]), min(icon_offset[1], text_offset[1])), msgsize

def _draw_footer(image, draw, text, font):
    dimensions = draw.textsize(text, font=font)
    offset = (EPD_WIDTH-dimensions[0], EPD_HEIGHT-dimensions[1])
    draw.text(offset, text, font=font, fill=BLACK)
    return offset, dimensions

def create(context):
    image = Image.new('L', (EPD_WIDTH, EPD_HEIGHT), WHITE)
    draw = ImageDraw.Draw(image)
    draw.fontmode = '1' # No Anti-aliasing
    fonts = {
        'header': ImageFont.truetype(local_file('fonts/FreeSansBold.ttf'), 36),
        'special': ImageFont.truetype(local_file('fonts/FreeSansBold.ttf'), 36),
        'temperature': ImageFont.truetype(local_file('fonts/FreeSans.ttf'), 24),
        'calendar_header': ImageFont.truetype(local_file('fonts/FreeSans.ttf'), 20),
        'calendar_body': ImageFont.truetype(local_file('fonts/FreeSans.ttf'), 16),
        'footer': ImageFont.truetype(local_file('fonts/FreeSans.ttf'), 14),
    }

    # Footer: Bottom-right corner
    updated_msg = 'Updated ' + context['now'].strftime('%B %-m, %-I:%M %p') # %-m and %-I are platform specific
    footer_offset, footer_dimensions = _draw_footer(image, draw, updated_msg, fonts['footer'])

    # Special event, centered across whole display, above footer
    special_offset = None
    if context['today']['special_event'] and 'msg' in context['today']['special_event']:
        special_offset, special_dimensions = _draw_special_event(image, draw, context['today']['special_event'], footer_offset, fonts['special'])

    cal_bottom = (special_offset[1] if special_offset else (footer_offset[1])) - 1

    # 1st Column
    left = 0
    _draw_header(draw, (left, 0), context['today']['date'].strftime('%b %-m'), fonts['header'], RED)
    if context['today']['conditions'] and context['today']['forecast']: _draw_forecast_and_current(image, draw, context['today']['conditions'], context['today']['forecast'], fonts['header'], fonts['temperature'])
    if context['today']['events']: _draw_calendar(image, draw, context['today']['events'], (left, CALENDAR_TOP), cal_bottom, fonts['calendar_header'], fonts['calendar_body'])

    # 2nd Column
    left = COLUMN_WIDTH
    draw.line([(left, 0), (left, cal_bottom)], width=1, fill=BLACK)
    _draw_header(draw, (left, 0), context['plus_one']['date'].strftime('%a'), fonts['header'])
    if context['plus_one']['forecast']: _draw_forecast(image, draw, left, context['plus_one']['forecast'], fonts['header'], fonts['temperature'])
    if context['plus_one']['events']: _draw_calendar(image, draw, context['plus_one']['events'], (left, CALENDAR_TOP), cal_bottom, fonts['calendar_header'], fonts['calendar_body'])

    # 3rd Column
    left = COLUMN_WIDTH * 2
    draw.line([(left, 0), (left, cal_bottom)], width=1, fill=BLACK)
    _draw_header(draw, (left, 0), context['plus_two']['date'].strftime('%a'), fonts['header'])
    if context['plus_two']['forecast']: _draw_forecast(image, draw, left, context['plus_two']['forecast'], fonts['header'], fonts['temperature'])
    if context['plus_two']['events']: _draw_calendar(image, draw, context['plus_two']['events'], (left, CALENDAR_TOP), cal_bottom, fonts['calendar_header'], fonts['calendar_body'])

    # 4th Column
    left = COLUMN_WIDTH * 3
    draw.line([(left, 0), (left, cal_bottom)], width=1, fill=BLACK)
    _draw_header(draw, (left, 0), context['plus_three']['date'].strftime('%a'), fonts['header'])
    if context['plus_three']['forecast']: _draw_forecast(image, draw, left, context['plus_three']['forecast'], fonts['header'], fonts['temperature'])
    if context['plus_three']['events']: _draw_calendar(image, draw, context['plus_three']['events'], (left, CALENDAR_TOP), cal_bottom, fonts['calendar_header'], fonts['calendar_body'])

    return image
