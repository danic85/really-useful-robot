import pigpio
from time import sleep

class Servo:
    def __init__(self, pin, pwmRange, startPos=50):
        self.pin = pin
        self.range = pwmRange
        self.pi = pigpio.pi()
        self.pi.set_mode(pin, pigpio.OUTPUT)
        self.start = startPos
        self.move(self.start)
    
    def move(self, percent):
        if percent < 0:
            percent = 0
        if percent > 100:
            percent = 100
            
        print(self.translate(percent));
        self.pi.set_servo_pulsewidth(self.pin, self.translate(percent))
        sleep(0.5) # @todo calculate time required to reach
        
    def reset(self):
        self.move(self.start)
    
    def translate(self, value):
        # Figure out how 'wide' each range is
        leftSpan = 100 - 0
        rightSpan = self.range[1] - self.range[0]

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return self.range[0] + (valueScaled * rightSpan)