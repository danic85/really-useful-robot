
from modules.led import RGBLED
from modules.servo import Servo
from modules.thread_manager import thread_manager

# Initialise modules
led = RGBLED(24, 23, 18)
threads = thread_manager()

# @todo set initial positions in config file
pan = Servo(21, 1540)
tilt = Servo(20, 1330)
bounce = Servo(16, 0)

# Main loop
try:
    while True:
        threads.add_thread('breathe', led.breathe, 'blue')
        pass

except KeyboardInterrupt:
        pass
