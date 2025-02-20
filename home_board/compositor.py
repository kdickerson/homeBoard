# Generate in image from the provided weather, calendar, special_events data
import logging
import os

from PIL import Image, ImageDraw, ImageFont

from .util import local_file

EPD_WIDTH = 640
EPD_HEIGHT = 384
BLACK = 0
WHITE = 255
RED = 128

COLUMN_WIDTH = 160
COLUMNS = [0, COLUMN_WIDTH, COLUMN_WIDTH * 2, COLUMN_WIDTH * 3]
HEADER_TOP = 0
WEATHER_TEMP_TOP = 37
WEATHER_ICON_TOP = 61
CALENDAR_TOP = 130

WEATHER_ICON_MAP = {
    'chanceflurries': 'chancesnow.bmp',
    'chancerain': 'chancerain.bmp',
    'chancesleet': 'chancesnow.bmp',
    'chancesnow': 'chancesnow.bmp',
    'chancetstorms': 'chancetstorms.bmp',
    'clear': 'sunny.bmp',
    'cloudy': 'cloudy.bmp',
    'cloudy_windy': 'cloudy_windy.bmp',
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
    'windy': 'windy.bmp',
}

EVENT_ICON_MAP = {
    'birthday': 'birthday.bmp',
    'christmas': 'christmas.bmp',
    'flag': 'flag.bmp',
    'halloween': 'halloween.bmp',
    'heart': 'heart.bmp',
    'thanksgiving': 'thanksgiving.bmp',
}

WEATHER_ICON_PATH = 'icons/weather/'
EVENTS_ICON_PATH = 'icons/events/'
BLACK_TO_RED_LUT = [RED] + ([BLACK] * 254) + [WHITE]  # Map BLACK to RED, leave WHITE alone; use with Image.point()


def _load_weather_icon(icon):
    # Expecting 64x64 monochrome icons
    return Image.open(local_file(os.path.join(WEATHER_ICON_PATH, WEATHER_ICON_MAP[icon])))


def _load_event_icon(icon):
    return Image.open(local_file(os.path.join(EVENTS_ICON_PATH, EVENT_ICON_MAP[icon])))


def _draw_centered_text(draw, offset, width, text, font, color=BLACK, measure_text=None):
    text_width = draw.textlength(measure_text if measure_text else text, font=font)
    loc = ((width - text_width) // 2 + offset[0], offset[1])
    draw.text(loc, text, font=font, fill=color)


def _truncate_text(draw, text, font, width):
    text_width = draw.textlength(text, font=font)
    i = 0
    while text_width > width:
        i = i - 1
        text_width = draw.textlength(text[:i], font=font)
    return (text[:i-1] + '…') if i < 0 else text, (text_width, font.size)


def _draw_header(draw, offset, text, font, color=BLACK):
    _draw_centered_text(draw, offset, COLUMN_WIDTH, text, font, color)


def _draw_calendar(image, draw, events, offset, bottom, cal_header_font, description_font):
    logging.debug('_draw_calendar:start')
    time_left_margin = 5
    text_left_margin = 5
    right_margin = 5
    bottom_margin = 5
    top = offset[1]
    more_msg_height = description_font.size
    for idx, event in enumerate(events):
        header_txt = ''
        # Make sure we don't show start times for events that started a previous date,
        #  don't show end times for events ending a future date
        if not event['all_day']:
            if event['underway']:
                if event['ending_days_away'] == 0:
                    header_txt = '→' + event['end'].strftime('%-H:%M') + ' '  # %-H is Linux specific
                elif event['ending_days_away'] > 0:
                    header_txt = '+' + str(event['ending_days_away']) + ' Day' + \
                        ('' if event['ending_days_away'] == 1 else 's') + ' '
            else:
                header_txt = event['start'].strftime('%-H:%M') + ' '  # %-H is Linux specific
        header_txt += event['calendar_label']

        header, header_dim = _truncate_text(
            draw,
            header_txt,
            cal_header_font,
            COLUMN_WIDTH - right_margin - time_left_margin
        )
        desc, desc_dim = _truncate_text(
            draw,
            event['description'],
            description_font,
            COLUMN_WIDTH - right_margin - text_left_margin
        )

        if top + header_dim[1] + desc_dim[1] + (0 if idx+1 == len(events) else more_msg_height) > bottom:
            more_msg = '+' + str(len(events) - idx) + ' More'
            _draw_centered_text(draw, (offset[0], top), COLUMN_WIDTH, more_msg, description_font)
            break
        draw.text(
            (offset[0] + time_left_margin, top),
            header,
            font=cal_header_font,
            fill=RED if event['underway'] else BLACK
        )
        draw.text(
            (offset[0] + text_left_margin, top + header_dim[1]),
            desc,
            font=description_font,
            fill=RED if event['underway'] else BLACK
        )
        top = top + header_dim[1] + desc_dim[1] + bottom_margin
    logging.debug('_draw_calendar:end')


def _draw_forecast_and_current(image, draw, conditions, forecast, header_font, temp_font):
    logging.debug('_draw_forecast_and_current:start')
    logging.debug('current: ' + str(conditions))
    logging.debug('forecast: ' + str(forecast))
    SUB_COLUMN_WIDTH = COLUMN_WIDTH // 2
    cur_icon = None
    forecast_icon = None

    # Sub column 1:
    if conditions:
        _draw_centered_text(
            draw,
            (0, WEATHER_TEMP_TOP),
            SUB_COLUMN_WIDTH,
            str(conditions['temperature']) + '°',
            temp_font,
            color=RED,
            measure_text=str(conditions['temperature'])
        )
        try:
            cur_icon = _load_weather_icon(conditions['icon']).point(BLACK_TO_RED_LUT)
            image.paste(cur_icon, ((SUB_COLUMN_WIDTH - cur_icon.size[0]) // 2, WEATHER_ICON_TOP))
        except Exception:
            cur_icon = None

    # Sub column 2:
    if forecast:
        _draw_centered_text(
            draw,
            (SUB_COLUMN_WIDTH, WEATHER_TEMP_TOP),
            SUB_COLUMN_WIDTH,
            str(forecast['high-temperature']) + '°',
            temp_font,
            measure_text=str(forecast['high-temperature'])
        )
        try:
            forecast_icon = _load_weather_icon(forecast['icon'])
            image.paste(forecast_icon,
                        ((SUB_COLUMN_WIDTH - cur_icon.size[0]) // 2 + SUB_COLUMN_WIDTH, WEATHER_ICON_TOP))
        except Exception:
            forecast_icon = None

    if not cur_icon and not forecast_icon and conditions:
        _draw_centered_text(draw, (0, WEATHER_ICON_TOP), COLUMN_WIDTH, conditions['description'], temp_font)
    logging.debug('_draw_forecast_and_current:end')


def _draw_forecast(image, draw, column_left, forecast, header_font, temp_font):
    logging.debug('_draw_forecast:start')
    logging.debug('forecast: ' + str(forecast))
    msg = str(forecast['low-temperature']) + '–' + str(forecast['high-temperature'])  # Center before adding the °
    _draw_centered_text(draw, (column_left, WEATHER_TEMP_TOP), COLUMN_WIDTH, msg + '°', temp_font, measure_text=msg)
    try:
        icon = _load_weather_icon(forecast['icon'])
        image.paste(icon, ((COLUMN_WIDTH - icon.size[0]) // 2 + column_left, WEATHER_ICON_TOP))
    except:  # noqa: E722
        _draw_centered_text(draw, (column_left, WEATHER_ICON_TOP), COLUMN_WIDTH, forecast['description'], temp_font)
    logging.debug('_draw_forecast:end')


def _draw_special_event(image, draw, event, footer_offset, font):
    logging.debug('_draw_special_event:start')
    width = draw.textlength(event['msg'], font=font)
    height = font.size
    iconsize = (0, 0)
    icon = None
    try:
        icon = _load_event_icon(event['icon']) if 'icon' in event else None
        if icon:
            iconsize = icon.size
    except:  # noqa: E722
        raise

    if icon:
        padding = 5
        msgsize = (iconsize[0] + width + padding, max(height, iconsize[1]))
    else:
        padding = 0
        msgsize = (width, height)

    icon_left = (EPD_WIDTH - msgsize[0]) // 2
    icon_top = footer_offset[1] - msgsize[1]
    icon_offset = (round(icon_left), round(icon_top + (msgsize[1] - iconsize[1]) // 2))
    text_offset = (round(icon_left + iconsize[0] + padding), round(icon_top + (msgsize[1] - height) // 2))
    text_to_footer_gap = round(footer_offset[1] - (text_offset[1] + height))
    if text_to_footer_gap > 0:
        icon_offset = (icon_offset[0], icon_offset[1] + text_to_footer_gap)
        text_offset = (text_offset[0], text_offset[1] + text_to_footer_gap)
    image.paste(icon, icon_offset) if icon else None
    draw.text(text_offset, event['msg'], font=font, fill=RED)
    logging.debug('_draw_special_event:end')
    return (min(icon_offset[0], text_offset[0]), min(icon_offset[1], text_offset[1])), msgsize


def _draw_footer(image, draw, text, font):
    logging.debug('_draw_footer:start')
    width = draw.textlength(text, font=font)
    height = font.size
    offset = (EPD_WIDTH-width, EPD_HEIGHT-height)
    draw.text(offset, text, font=font, fill=BLACK)
    logging.debug('_draw_footer:end')
    return offset, (width, height)


def create(context):
    logging.debug('create:start')
    image = Image.new('L', (EPD_WIDTH, EPD_HEIGHT), WHITE)
    draw = ImageDraw.Draw(image)
    draw.fontmode = '1'  # No Anti-aliasing
    fonts = {
        'header': ImageFont.truetype(local_file('fonts/FreeSansBold.ttf'), 36),
        'special': ImageFont.truetype(local_file('fonts/FreeSansBold.ttf'), 36),
        'temperature': ImageFont.truetype(local_file('fonts/FreeSans.ttf'), 24),
        'calendar_header': ImageFont.truetype(local_file('fonts/FreeSans.ttf'), 20),
        'calendar_body': ImageFont.truetype(local_file('fonts/FreeSans.ttf'), 16),
        'footer': ImageFont.truetype(local_file('fonts/FreeSans.ttf'), 14),
    }

    # Footer: Bottom-right corner
    updated_msg = 'Updated ' + context['now'].strftime('%B %-d, %-I:%M %p')  # %-d and %-I are platform specific
    if not all(context['success'].values()):
        updated_msg = '[! ' + ','.join(sorted([k for k, v in context['success'].items() if not v])) + ']' + updated_msg
    footer_offset, footer_dimensions = _draw_footer(image, draw, updated_msg, fonts['footer'])

    # Special event, centered across whole display, above footer
    special_offset = None
    if context['today']['special_event'] and 'msg' in context['today']['special_event']:
        special_offset, special_dimensions = _draw_special_event(
            image,
            draw,
            context['today']['special_event'],
            footer_offset,
            fonts['special']
        )

    cal_bottom = (special_offset[1] if special_offset else footer_offset[1]) - 1

    # 1st Column
    left = COLUMNS[0]
    _draw_header(draw, (left, HEADER_TOP), context['today']['date'].strftime('%b %-d'), fonts['header'], RED)
    if context['today']['conditions'] or context['today']['forecast']:
        _draw_forecast_and_current(
            image,
            draw,
            context['today']['conditions'],
            context['today']['forecast'],
            fonts['header'],
            fonts['temperature']
        )
    if context['today']['events']:
        _draw_calendar(
            image,
            draw,
            context['today']['events'],
            (left, CALENDAR_TOP),
            cal_bottom,
            fonts['calendar_header'],
            fonts['calendar_body']
        )

    # 2nd Column
    left = COLUMNS[1]
    draw.line([(left, 0), (left, cal_bottom)], width=1, fill=BLACK)
    _draw_header(draw, (left, HEADER_TOP), context['plus_one']['date'].strftime('%a'), fonts['header'])
    if context['plus_one']['forecast']:
        _draw_forecast(image, draw, left, context['plus_one']['forecast'], fonts['header'], fonts['temperature'])
    if context['plus_one']['events']:
        _draw_calendar(
            image,
            draw,
            context['plus_one']['events'],
            (left, CALENDAR_TOP),
            cal_bottom,
            fonts['calendar_header'],
            fonts['calendar_body']
        )

    # 3rd Column
    left = COLUMNS[2]
    draw.line([(left, 0), (left, cal_bottom)], width=1, fill=BLACK)
    _draw_header(draw, (left, HEADER_TOP), context['plus_two']['date'].strftime('%a'), fonts['header'])
    if context['plus_two']['forecast']:
        _draw_forecast(image, draw, left, context['plus_two']['forecast'], fonts['header'], fonts['temperature'])
    if context['plus_two']['events']:
        _draw_calendar(
            image,
            draw,
            context['plus_two']['events'],
            (left, CALENDAR_TOP),
            cal_bottom,
            fonts['calendar_header'],
            fonts['calendar_body']
        )

    # 4th Column
    left = COLUMNS[3]
    draw.line([(left, 0), (left, cal_bottom)], width=1, fill=BLACK)
    _draw_header(draw, (left, HEADER_TOP), context['plus_three']['date'].strftime('%a'), fonts['header'])
    if context['plus_three']['forecast']:
        _draw_forecast(image, draw, left, context['plus_three']['forecast'], fonts['header'], fonts['temperature'])
    if context['plus_three']['events']:
        _draw_calendar(
            image,
            draw,
            context['plus_three']['events'],
            (left, CALENDAR_TOP),
            cal_bottom,
            fonts['calendar_header'],
            fonts['calendar_body']
        )

    logging.debug('create:end')
    return image
