
from modules.led import RGBLED
from modules.servo import Servo
from modules.idle import Idle
from modules.config import Config
# from modules.thread_manager import thread_manager

cfg = Config()

# Initialise modules
led = RGBLED(cfg.get('LEDR'), cfg.get('LEDG'), cfg.get('LEDB'))
# threads = thread_manager()

# @todo set initial positions in config file
pan = Servo(cfg.get('PAN'), 1540)
tilt = Servo(cfg.get('TILT'), 1330)
bounce = Servo(cfg.get('BOUNCE'), 0)
idle = Idle(cfg.get('MOTION'), 360)  # shutdown after 5 minutes, wake up with any movement unless switch disabled

# Main loop
try:
    while True:
        led.breathe('blue')
        # threads.add_thread('breathe', led.breathe, 'blue')
        pass

except KeyboardInterrupt:
        pass
