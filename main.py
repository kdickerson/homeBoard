import weather
import calendar
import special_events
import compositor
import datetime
import sys

def make_image(when):
    conditions = weather.fetch(when)
    calendering = calendar.fetch(when)
    special_event = special_events.fetch(when)
    return compositor.create(conditions, calendering, special_event)

def display_image():
    import epd7in5b
    epd = epd7in5b.EPD()
    epd.init()
    now = datetime.datetime.now()
    image = make_image(now)
    epd.display_frame(epd.get_frame_buffer(image))

def save_image():
    #when = datetime.datetime(2018, 3, 17, 17, 16)
    when = datetime.datetime.now()
    image = make_image(when)
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
