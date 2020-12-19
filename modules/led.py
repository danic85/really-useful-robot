from pubsub import pub
from modules.config import Config
from modules.arduinoserial import ArduinoSerial
from time import sleep
import threading

class LED:
    COLOUR_OFF = (0, 0, 0)
    COLOUR_RED = (5, 0, 0)
    COLOUR_GREEN = (0, 5, 0)
    COLOUR_BLUE = (0, 0, 5)
    COLOUR_WHITE = (255, 255, 255)

    COLOUR_MAP = {
        'red': COLOUR_RED,
        'green': COLOUR_GREEN,
        'blue': COLOUR_BLUE,
        'white': COLOUR_WHITE,
        'off': COLOUR_OFF
    }

    def __init__(self, count, **kwargs):
        self.count = count
        self.middle = kwargs.get('middle', 0)
        self.all = range(self.count)
        pub.subscribe(self.set, 'led')
        pub.subscribe(self.spinner, 'led:spinner')
        self.set(self.all, LED.COLOUR_OFF)
        sleep(0.1)
        self.set(self.middle, LED.COLOUR_GREEN)
        self.animation = False
        self.thread = None

    def exit(self):
        self.animation = False
        self.thread.join()
        self.set(Config.LED_ALL, LED.COLOUR_OFF)
        sleep(1)

    def set(self, identifiers, color):
        """
        Set color of pixel
        (255, 0, 0) # set to red, full brightness
        (0, 128, 0) # set to green, half brightness
        (0, 0, 64)  # set to blue, quarter brightness
        :param number: pixel number (starting from 0) - can be list
        :param color: (R, G, B)
        """
        pub.sendMessage('serial', type=ArduinoSerial.DEVICE_LED, identifier=identifiers, message=color)

    def flashlight(self, on):
        if on:
            self.set(self.all, LED.COLOUR_WHITE)
        else:
            self.set(self.all, LED.COLOUR_OFF)
            sleep(0.1)
            self.eye('green')

    def eye(self, color):
        if color in LED.COLOUR_MAP.keys():
            print(LED.COLOUR_MAP[color])
            self.set(self.middle, LED.COLOUR_MAP[color])

    def spinner(self, color):

        if not color and self.animation:
            print('SPINNER STOPPING')
            self.thread.join()
            self.animation = False
            return

        if self.animation:
            print('SPINNER ALREADY STARTED')
            return

        print('SPINNER STARTING')
        self.thread = threading.Thread(target=self.spinner_animate, args=(color,))
        self.thread.start()
        self.animation = True


    def spinner_animate(self, color, index=1):
        sleep(.3)

        self.set(range(1, 7), LED.COLOUR_OFF)
        self.set(index, LED.COLOUR_MAP[color])

        index = (index + 1) % self.count
        # don't set the center led
        if index == 0:
            index = 1

        if self.animation:
            self.spinner_animate(color, index)
