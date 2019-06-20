import pigpio
import time

class RGBLED:

    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue

        self.pi = pigpio.pi()
        self.pi.set_mode(red, pigpio.OUTPUT)
        self.pi.set_mode(green, pigpio.OUTPUT)
        self.pi.set_mode(blue, pigpio.OUTPUT)

    def __del__(self):
        self.led('red', 0)
        self.led('green', 0)
        self.led('blue', 0)

    def get_color_pin(self, colorname):
        if colorname is 'red':
            return self.red
        elif colorname is 'green':
            return self.green
        elif colorname is 'blue':
            return self.blue
        raise ValueError('Colour %s is not valid', colorname)

    def breathe(self, color, start=0, increment=2, lighter=True):
        while start >= 0:
            self.led(color, start)
            if lighter is True:
                start = start + increment
            else:
                start = start - increment
            if start >= 100:
                lighter = not lighter
                start = 100
                time.sleep(1)
            time.sleep(0.05)
        time.sleep(1)

    def led(self, color, percent):
        if 0 <= percent <= 100:
            return self.pi.set_PWM_dutycycle(self.get_color_pin(color), 255*(percent/100))
        raise ValueError('Percent %d is not in range' % percent)
