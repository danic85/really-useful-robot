import RPi
import subprocess
import threading

# Detect motion from PIR or microwave sensor on pin MOTION_PIN
# Also supports switch. If input of MOTION_PIN is set to HIGH (switch on), shutdown timer is cancelled.
# If input is low, shutdown will occur in 60 seconds unless HIGH input is received again from switch or motion sensor.


class Idle:
    def detect_motion(self):
        if RPi.GPIO.input(self.pin):
            # print("Rising")
            self.timer.cancel()

        else:
            # print("Falling")
            self.timer.start()

    def shutdown(self):
        return subprocess.call(['shutdown', '-h', 'now'], shell=False)

    def __init__(self, pin, timeout):
        self.pin = pin
        self.timeout = timeout
        self.timer = threading.Timer(self.timeout, self.shutdown)
        RPi.GPIO.setmode(RPi.GPIO.BCM)  # set up BCM GPIO numbering
        RPi.GPIO.setup(self.pin, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)
        RPi.GPIO.add_event_detect(self.pin, RPi.GPIO.BOTH, callback=self.detect_motion)















