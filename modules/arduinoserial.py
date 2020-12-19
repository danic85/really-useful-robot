from __future__ import print_function, division, absolute_import
import time
from modules.robust_serial.robust_serial import write_order, Order, write_i8, write_i16, read_i8, read_order
from modules.robust_serial.utils import open_serial_port, CustomQueue, queue
from modules.robust_serial.threads import CommandThread, ListenerThread
import threading
from pubsub import pub

rate = 1 / 2000  # 2000 Hz (limit the rate of communication with the arduino)

class ArduinoSerial:
    """
    Communicate with Arduino over Serial
    """
    DEVICE_LED = 0
    DEVICE_SERVO = 1
    DEVICE_PIN = 2
    DEVICE_PIN_READ = 3

    def __init__(self, **kwargs):
        self.serial_file = ArduinoSerial.initialise()
        self.file = None
        pub.subscribe(self.send, 'serial')

        # Create Command queue for sending orders
        self.command_queue = CustomQueue(2)
        # Number of messages we can send to the Arduino without receiving an acknowledgment
        self.n_messages_allowed = 3
        self.n_received_semaphore = threading.Semaphore(self.n_messages_allowed)
        # Lock for accessing serial file (to avoid reading and writing at the same time)
        self.serial_lock = threading.Lock()

        # Event to notify threads that they should terminate
        self.exit_event = threading.Event()

        threads = [ArduinoCommandThread(self.serial_file, self.command_queue, self.exit_event, self.n_received_semaphore, self.serial_lock),
                   ListenerThread(self.serial_file, self.exit_event, self.n_received_semaphore, self.serial_lock)]
        for t in threads:
            t.start()


    @staticmethod
    def initialise():
        try:
            serial_file = open_serial_port(baudrate=115200, timeout=None)
        except Exception as e:
            raise e

        is_connected = False
        # Initialize communication with Arduino
        while not is_connected:
            print("Waiting for arduino...")
            write_order(serial_file, Order.HELLO)
            bytes_array = bytearray(serial_file.read(1))
            if not bytes_array:
                time.sleep(2)
                continue
            byte = bytes_array[0]
            if byte in [Order.HELLO.value, Order.ALREADY_CONNECTED.value]:
                is_connected = True

        print("Connected to Arduino")
        return serial_file

    def send(self, type, identifier, message):
        """
        Examples:
        # send(ArduinoSerial.DEVICE_SERVO, 18, 20)
        # send(ArduinoSerial.DEVICE_LED, 1, (20,20,20))
        # send(ArduinoSerial.DEVICE_LED, range(9), (20,20,20))
        :param type: one of the DEVICE_ types
        :param identifier: an identifier or list / range of identifiers, pin or LED number
        :param message: the packet to send to the arduino
        """
        print('serial queueing ' + str(type) + ' - ' + str(identifier) + ' = ' + str(message))
        self.command_queue.put((type, identifier, message))


class ArduinoCommandThread(CommandThread):
    def run(self):
        while not self.exit_event.is_set():
            self.n_received_semaphore.acquire()
            if self.exit_event.is_set():
                break
            try:
                type, identifier, message = self.command_queue.get_nowait()
            except queue.Empty:
                time.sleep(rate)
                self.n_received_semaphore.release()
                continue

            with self.serial_lock:
                if type == ArduinoSerial.DEVICE_SERVO:
                    write_order(self.serial_file, Order.SERVO)
                    write_i8(self.serial_file, identifier)
                    write_i16(self.serial_file, int(message))
                elif type == ArduinoSerial.DEVICE_LED:
                    write_order(self.serial_file, Order.LED)
                    if isinstance(identifier, list) or isinstance(identifier, range):
                        # write the number of leds to update
                        write_i8(self.serial_file, len(identifier))
                        for i in identifier:
                            write_i8(self.serial_file, i)
                    else:
                        write_i8(self.serial_file, 1)
                        write_i8(self.serial_file, identifier)

                    if isinstance(message, tuple):
                        for v in message:
                            write_i8(self.serial_file, v)
                    else:
                        write_i16(self.serial_file, message)

                elif type == ArduinoSerial.DEVICE_PIN:
                    write_order(self.serial_file, Order.PIN)
                    write_i8(self.serial_file, identifier)
                    write_i8(self.serial_file, message)

                # elif type == ArduinoSerial.DEVICE_PIN_READ:
                #     write_order(self.serial_file, Order.READ)
                #     write_i8(self.serial_file, identifier)
                #     value = read_i8(self.serial_file)
                #     return value
            time.sleep(rate)
