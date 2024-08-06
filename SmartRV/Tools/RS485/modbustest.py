import sys
import time

import minimalmodbus

try:
    PORT=sys.argv[1]
except IndexError:
    PORT='/dev/ttymxc1'


COMMANDS = {
    0x00: 'AC_VOLTAGE',
    0x08: 'AC_CURRENT',
    0x12: 'ACTIVE_POWER',
    0x1A: 'REACTIVE_POWER',
    0x2A: 'Power Factor',
    0x36: 'Frequency',
    0x100: 'Total Active Power',
    0x200: 'Total Reactive Power'
}

TEMP_REGISTER = 100
HUM_REGISTER = 102
AC_CURRENT = 8
AC_VOLTAGE = 0
ACTIVE_POWER = 0x12
CUSTOM = 0x0036
BAUD_RATE = 0

#Set up instrument
instrument = minimalmodbus.Instrument(
    PORT,
    11,
    mode=minimalmodbus.MODE_RTU
)

# instrument.handle_local_echo=True
# instrument.debug=True
#Make the settings explicit
instrument.serial.baudrate = 9600        # Baud
instrument.serial.bytesize = 8
instrument.serial.parity   = minimalmodbus.serial.PARITY_EVEN
instrument.serial.stopbits = 1
instrument.serial.timeout  = 1          # seconds

# Good practice
instrument.close_port_after_each_call = True
instrument.clear_buffers_before_each_transaction = True

# # if you need to read a 16 bit register use instrument.read_register()
# try:
#     current = instrument.read_float(AC_CURRENT, functioncode=4)
#     print('Current', current)
# except Exception as err:
#     print(err)

# try:
#     voltage = instrument.read_float(AC_VOLTAGE, functioncode=4)
#     print('Voltage', voltage)
# except minimalmodbus.InvalidResponseError as err:
#     print(err)


# try:
#     active_power = instrument.read_float(ACTIVE_POWER, functioncode=4)
#     print('Active Power (kWh)', active_power)
# except minimalmodbus.InvalidResponseError as err:
#     print(err)
    
# try:
#     custom = instrument.read_float(CUSTOM, functioncode=4)
#     print(CUSTOM, custom)
# except minimalmodbus.InvalidResponseError as err:
#     print(err)


# print(instrument.write_register(0x10, 0.0, number_of_decimals=1))


# for cmd in (0x0, 0x2, 0x8, 10, 0x10):
#     try:
#         response = instrument.read_float(cmd, functioncode=3)
#         print(cmd, response)
#     except minimalmodbus.InvalidResponseError as err:
#         print(err)


for cmd, name in COMMANDS.items():
    print(name, instrument.read_float(cmd, functioncode=4))
    
# for cmd in range(100):
#     print(cmd, instrument.read_float(cmd, functioncode=4))

# value = 0.0
# last_delta_time = 0.0
# while True:
#     result = instrument.read_float(0x100, functioncode=4)
#     delta = result - value
#     print(time.time(), result, 'Delta', delta)
#     if delta:
#         delta_time = time.time() - last_delta_time
#         watts = delta * 1000 * 3600 / delta_time
#         print('\t', watts, '(', delta_time, ')')
#         last_delta_time = time.time()    
#         value = result
#     time.sleep(5)
    