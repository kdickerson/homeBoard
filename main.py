from home_board import weather, calendar, special_events, compositor
import datetime
import sys

def make_image():
    conditions = weather.fetch()
    calender_events = calendar.fetch()
    special_event = special_events.fetch()
    return compositor.create(conditions, calender_events, special_event)

def display_image():
    from waveshare import epd7in5b
    epd = epd7in5b.EPD()
    epd.init()
    image = make_image()
    epd.display_frame(epd.get_frame_buffer(image))

def save_image():
    image = make_image()
    image.save('composite.bmp')

'''
    Save image rather than send to display (for quick testing of design changes):
    python main.py save
'''
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'save':
        save_image()
    else:
        display_image()
