# Generate in image from the provided weather, calendar, special_events data
from PIL import Image, ImageDraw, ImageFont

EPD_WIDTH = 640
EPD_HEIGHT = 384
BLACK = 0
WHITE = 255
RED = 128

# TODO: Generate subroutines to fill in subsections by size, then composite those sections back together
# Which should allow me to much more easily align things to edges

def create(weather, calendar, special_event):
    image = Image.new('L', (EPD_WIDTH, EPD_HEIGHT), WHITE)    # 255: clear the frame
    draw = ImageDraw.Draw(image)
    header_font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf', 36)
    body_font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf', 24)

    draw.text((0, 10), 'Current', font=header_font, fill=BLACK)
    draw.text((0, 100), str(weather['current']['temperature']) + ' F', font=body_font, fill=BLACK)
    draw.text((0, 150), str(weather['current']['wind']) + ' MPH', font=body_font, fill=BLACK)

    draw.text((250, 10), 'Today', font=header_font, fill=BLACK)
    draw.text((250, 100), 'High: ' + str(weather['forecast']['today']['high-temperature']) + ' F', font=body_font, fill=BLACK)
    draw.text((250, 150), 'Low: ' + str(weather['forecast']['today']['low-temperature']) + ' F', font=body_font, fill=BLACK)

    draw.text((475, 10), 'Tomorrow', font=header_font, fill=BLACK)
    draw.text((475, 100), 'High: ' + str(weather['forecast']['tomorrow']['high-temperature']) + ' F', font=body_font, fill=BLACK)
    draw.text((475, 150), 'Low: ' + str(weather['forecast']['tomorrow']['low-temperature']) + ' F', font=body_font, fill=BLACK)

    if (special_event):
        draw.text((0, 300), special_event['name'], font=header_font, fill=RED)

    return image
