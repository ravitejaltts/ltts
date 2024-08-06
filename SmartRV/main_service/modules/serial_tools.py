import serial
import threading


A_READ_AIR_PRESSURE = 'a'
A_READ_ACCELEROMETER = 'b'
A_READ_ALTITUDE = 'c'
A_READ_TEMPERATURE = 'd'
A_SET_LED = 'e'
A_SET_OUTLET = 'f'
A_SET_CHARGER = 'k'


RETURNS = [
    A_READ_TEMPERATURE,
    A_READ_ACCELEROMETER,
    A_READ_AIR_PRESSURE,
    A_READ_ALTITUDE
]


def print_line(line, request):
    print(request, line.decode('utf8').strip())


class ArduinoHandler(object):
    def __init__(self, port, speed=9600):
        self.port = port
        self.speed = speed
        self.serial = self.openConnection()
        self.pending_request = None

    def openConnection(self):
        return serial.Serial(port=self.port, baudrate=self.speed)

    def readLoop(self, callback):
        while True:
            line = self.serial.readline()
            if self.pending_request:
                self.pending_request = None
                callback(line, self.pending_request)

    def send(self, command):
        if command in RETURNS:
            self.pending_request = command

        self.serial.write(command.encode('utf8'))

    def read_all(self):
        for command in (
            A_READ_ALTITUDE,
            A_READ_ACCELEROMETER,
            A_READ_AIR_PRESSURE,
            A_READ_TEMPERATURE
        ):
            pass


if __name__ == '__main__':
    import time
    handler = ArduinoHandler('/dev/ttyACM0', 9600)

    th = threading.Thread(
        target=handler.readLoop,
        args=[print_line,]
    )
    th.start()

    handler.send(f'{A_SET_OUTLET}0')
    handler.send(f'{A_SET_OUTLET}1')

    for i in range(5):
        handler.send('e1')
        time.sleep(1)
        handler.send('e0')
        time.sleep(1)
        handler.send(A_READ_TEMPERATURE)
        time.sleep(1)
        handler.send(A_READ_ACCELEROMETER)
        time.sleep(1)
        handler.send(A_READ_AIR_PRESSURE)
        time.sleep(1)
        handler.send(A_READ_ALTITUDE)
        time.sleep(1)

    th.join()
