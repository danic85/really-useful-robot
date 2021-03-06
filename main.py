import os
from pubsub import pub
import logging
logging.basicConfig(filename=os.path.dirname(__file__) + '/app.log', level=logging.DEBUG, format='%(levelname)s: %(asctime)s %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p') # this doesn't work unless it's here
from modules.logwrapper import LogWrapper

try:
    import pigpio
except ModuleNotFoundError as e:
    from modules.mocks.mock_pigpio import MockPiGPIO
    import pigpio
    from modules.mocks.mock_cv2 import MockCV2

from time import sleep, time
import signal
import schedule

# Import modules
from modules.config import Config
from modules.actuators.servo import Servo
from modules.vision import Vision
from modules.tracking import Tracking
from modules.visionutils.train_model import TrainModel
from modules.animate import Animate
from modules.power import Power
from modules.keyboard import Keyboard
from modules.sensor import Sensor
try:
    from modules.hotword import HotWord
except ModuleNotFoundError as e:
    pass

import sys


from modules.speechinput import SpeechInput
from modules.arduinoserial import ArduinoSerial
from modules.led import LED
from modules.personality import Personality
from modules.battery import Battery
from modules.braillespeak import Braillespeak

def mode():
    if len(sys.argv) > 1 and sys.argv[1] == 'manual':
        return Config.MODE_KEYBOARD
    return Config.MODE_LIVE

def main():
    path = os.path.dirname(__file__)
    log = LogWrapper(path=os.path.dirname(__file__))

    # Throw exception to safely exit script when terminated
    signal.signal(signal.SIGTERM, Config.exit)

    # POWER
    power = Power(Config.POWER_ENABLE_PIN)

    # GPIO
    gpio = pigpio.pi()

    # Arduino connection
    serial = ArduinoSerial()

    power.use()
    sleep(2)  # @todo possible fix for PD bug

    servos = dict()
    for key in Config.servos:
        s = Config.servos[key]
        servos[key] = Servo(s['pin'], key, s['range'], start_pos=s['start'])

    led = LED(Config.LED_COUNT)

    if Config.MOTION_PIN is not None:
        motion = Sensor(Config.MOTION_PIN, pi=gpio)

    if mode() == Config.MODE_LIVE:
        # Vision / Tracking
        vision = Vision(mode=Vision.MODE_FACES, rotate=True, path=path)
        tracking = Tracking(vision)
        training = TrainModel(dataset=path + '/matches/trained', output='encodings.pickle.new')
    elif mode() == Config.MODE_KEYBOARD:
        keyboard = Keyboard()

    # Voice
    if Config.HOTWORD_MODEL is not None:
        hotword = HotWord(Config.HOTWORD_MODEL)
        hotword.start()  # @todo this starts the thread. can it be moved into hotword?
        hotword.start_recog(sleep_time=Config.HOTWORD_SLEEP_TIME)
        sleep(1)  # @todo is this needed?
        # @todo this is throwing errors: ALSA lib confmisc.c:1281:(snd_func_refer) Unable to find definition 'defaults.bluealsa.device'
        speech = SpeechInput()

    # Output
    if Config.BUZZER_PIN is not None:
        speak = Braillespeak(Config.BUZZER_PIN, duration=80/1000)

    animate = Animate()
    personality = Personality(mode=mode())
    # @todo 2k resistor needs switching to > 3k for 20v+ support.
    #battery = Battery(0, serial, path=path) # note: needs ref for pubsub to work

    # Nightly loop (for facial recognition model training)
    schedule.every().day.at("10:30").do(pub.sendMessage, 'loop:nightly')
    # Other more frequent loops
    second_loop = time()
    minute_loop = time()
    loop = True
    pub.sendMessage('log', msg="[Main] Loop started")
    try:
        while loop:
            pub.sendMessage('loop')
            if time() - second_loop > 1:
                second_loop = time()
                pub.sendMessage('loop:1')
            if time() - minute_loop > 60:
                minute_loop = time()
                pub.sendMessage('loop:60')
                schedule.run_pending()

    except (Exception) as e:
        pub.sendMessage('log:error', msg=e)
        loop = False
        sleep(5)
        quit()

    finally:
        pub.sendMessage("exit")
        pub.sendMessage("animate", action="sit")
        pub.sendMessage("animate", action="sleep")
        pub.sendMessage("power:exit")
        pub.sendMessage("log", msg="[Main] loop ended")

if __name__ == '__main__':
    main()
