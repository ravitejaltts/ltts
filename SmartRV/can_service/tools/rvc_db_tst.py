import cantools
from cantools.database.can.signal import NamedSignalValue
from pprint import pprint
import json

class SignalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, NamedSignalValue):
            return [obj.value, obj.name]
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

db = cantools.database.load_file('dbc/rvc.dbc')

pprint(db.messages)

for msg in db.messages:
    pprint(msg.signals)


pprint(db.decode_message(0x0DFFED51, b'\x00\x00\x00\x00\x00\xFF\xFF\xC0'))
pprint(db.decode_message(0x0DFFED51, b'\x48\x00\x00\x04\x00\xFF\xFF\xC0'))
pprint(db.decode_message(0x0DFFED51, b'\x03\x00\x00\x11\x11\xFF\xFF\xD0'))

msg = '03 00 00 11 11 FF FF C0'

msg = bytes([int(i, 16) for i in msg.split(' ')])
decoded = db.decode_message(0x0DFFED51, msg)
print(type(decoded))
print(dir(decoded))

for k, v in decoded.items():
    print(k, v, type(v))
    if isinstance(v, NamedSignalValue):
        print(dir(v))
        print(v.name, v.value)

print(json.dumps(
    decoded,
    indent=4,
    cls=SignalEncoder
))

msg = '11 51 00 00 A1 FF FF 0F'
msg = bytes([int(i, 16) for i in msg.split(' ')])
decoded = db.decode_message(0x19FECA51, msg)
print(json.dumps(
    decoded,
    indent=4,
    cls=SignalEncoder
))

msg = '00 00 00 00 00 FF FF D0'
msg = bytes([int(i, 16) for i in msg.split(' ')])
decoded = db.decode_message(0x0DFFED51, msg)
print(json.dumps(
    decoded,
    indent=4,
    cls=SignalEncoder
))

msg = '15 51 00 00 A1 FF FF 0F'
msg = bytes([int(i, 16) for i in msg.split(' ')])
decoded = db.decode_message(0x19FECA51, msg)
print(json.dumps(
    decoded,
    indent=4,
    cls=SignalEncoder
))
# pprint(db.decode_message(0x0DFFEC51, b'\x40\x55\x00\x00\x00'))
