from modules.arduinoserial import ArduinoSerial
from pubsub import pub
import threading
import subprocess

class Battery:

    BATTERY_THRESHOLD = -60  # max 100 (12.3v), min -60 (8.8v)
    MAX_READINGS = 10

    def __init__(self, pin, serial, **kwargs):
        self.pin = pin
        self.readings = []
        self.serial = serial
        pub.subscribe(self.reading, 'serial:receive')

        self.stopped = threading.Event()
        self.thread = threading.Thread(target=self.request_reading)
        self.thread.daemon = True
        self.thread.start()
        print('BATTERY: STARTING')

    def exit(self):
        self.stopped.stop()
        self.thread.join()

    def request_reading(self):

        while not self.stopped.wait(1):
            print('BATTERY: REQUESTING')
            self.serial.send(ArduinoSerial.DEVICE_PIN_READ, 0, 0)

    def reading(self, identifier, payload):
        if identifier != 0:
            return

        print('BATTERY: READING - ' + str(payload))
        if self.check(payload) < Battery.BATTERY_THRESHOLD and len(self.readings) == Battery.MAX_READINGS:
            print('SHUTDOWN!')
            pub.sendMessage('shutdown')
            subprocess.call(['shutdown', '-h'], shell=False)
            quit()

    def check(self, val):
        if val == 5.0:
            return 0
        self.readings.append(val)
        if len(self.readings) > Battery.MAX_READINGS:
            self.readings.pop(0)

        avg = sum(self.readings) / len(self.readings)

        print('BATTERY: ' + str(avg))
        return avg
