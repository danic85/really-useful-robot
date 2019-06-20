import pigpio
from time import sleep

# Manage single servo
# Example usage:
# from modules.servo import Servo
# sv1 = Servo(17)
# sv1.move(50) # move to 50% of range (center)
# sv1.get_pos()
# sv1.move(5, True) # Add 5% to position


class Servo:

    # Init with optional start position and defined range for pulsewidth
    def __init__(self, pin, start=20000, minimum=25, maximum=40000):
        self.pi = pigpio.pi()
        self.pi.set_mode(pin, pigpio.OUTPUT)
        self.pin = pin
        self.min = minimum
        self.max = maximum
        self.pos = start

    # Move servo to position, entered as percentage of servo range.
    # Enter value between 0 and 100
    def move(self, percentage, relative=False):
        if percentage <= 100 and (percentage >= 0 or relative is True):
            actual_val = self.__translate(percentage, 0, 100, self.min, self.max)
            if relative:
                return self.__set_pos_relative(actual_val)
            else:
                return self.__set_pos(actual_val)
        raise ValueError('Percentage %d out of range' % percentage)

    # Get current position
    def get_pos(self):
        return self.pos

    # Set position to new value
    def __set_pos(self, pos):
        if self.max >= pos >= self.min:
            self.pos = pos
            self.pi.set_servo_pulsewidth(self.pin, pos)
            sleep(0.25)
            return True
        raise ValueError('Value %d out of range' % pos)

    # Adjust position by set delta value
    def __set_pos_relative(self, delta):
        current = self.pi.get_servo_pulsewidth(self.pin)
        new = current + delta
        if self.max > new > self.min:
            self.pos = new
            self.pi.set_servo_pulsewidth(self.pin, new)
            sleep(0.25)
            return True
        raise ValueError('Relative value %d makes value %d out of range' % (delta, new))

    # Map value range to new range
    def __translate(self, value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)