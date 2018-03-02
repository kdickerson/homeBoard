# Generate in image from the provided weather, calendar, special_events data
from PIL import Image, ImageDraw, ImageFont

EPD_WIDTH = 640
EPD_HEIGHT = 384
BLACK = 0
WHITE = 255
RED = 128

# TODO: Generate subroutines to fill in subsections by size, then composite those sections back together
#       Which should allow me to much more easily align things to edges and distribute whitespace

def create(weather, calendar, special_event):
    image = Image.new('L', (EPD_WIDTH, EPD_HEIGHT), WHITE)    # 255: clear the frame
    draw = ImageDraw.Draw(image)
    header_font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf', 36)
    body_font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf', 24)
    detail_font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf', 14)

    # Bottom-right corner
    dimensions = draw.textsize(weather['current']['time'], font=detail_font)
    draw.text((EPD_WIDTH-dimensions[0], EPD_HEIGHT-dimensions[1]), weather['current']['time'], font=detail_font, fill=BLACK)

    COLUMN_WIDTH = 213
    # Left Column
    dimensions = draw.textsize('Current', font=header_font)
    draw.text(((COLUMN_WIDTH-dimensions[0])/2, 0), 'Current', font=header_font, fill=BLACK)
    draw.text((0, 40), str(weather['current']['temperature']) + ' F', font=body_font, fill=BLACK)
    draw.text((0, 65), str(weather['current']['wind']) + ' MPH', font=body_font, fill=BLACK)
    draw.text((0, 90), weather['current']['description'], font=body_font, fill=BLACK)
    if weather['current']['icon']:
        image.paste(weather['current']['icon'], (0, 115))

    # Center Column
    dimensions = draw.textsize('Today', font=header_font)
    draw.text(((COLUMN_WIDTH-dimensions[0])/2 + 213, 0), 'Today', font=header_font, fill=BLACK)
    draw.text((213, 40), 'High: ' + str(weather['forecast']['today']['high-temperature']) + ' F', font=body_font, fill=BLACK)
    draw.text((213, 65), 'Low: ' + str(weather['forecast']['today']['low-temperature']) + ' F', font=body_font, fill=BLACK)
    draw.text((213, 90), weather['forecast']['today']['description'], font=body_font, fill=BLACK)
    if weather['forecast']['today']['icon']:
        image.paste(weather['forecast']['today']['icon'], (250, 115))

    # Right Column
    dimensions = draw.textsize('Tomorrow', font=header_font)
    draw.text(((COLUMN_WIDTH-dimensions[0])/2 + 427, 0), 'Tomorrow', font=header_font, fill=BLACK)
    draw.text((427, 40), 'High: ' + str(weather['forecast']['tomorrow']['high-temperature']) + ' F', font=body_font, fill=BLACK)
    draw.text((427, 65), 'Low: ' + str(weather['forecast']['tomorrow']['low-temperature']) + ' F', font=body_font, fill=BLACK)
    draw.text((427, 90), weather['forecast']['tomorrow']['description'], font=body_font, fill=BLACK)
    if weather['forecast']['tomorrow']['icon']:
        image.paste(weather['forecast']['tomorrow']['icon'], (475, 115))

    if (special_event):
        draw.text((0, 300), special_event['name'], font=header_font, fill=RED)

    return image
