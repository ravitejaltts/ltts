import base64
import sys


in_file = sys.argv[1]

encoded = base64.b64encode(open(in_file, 'rb').read())
print(encoded)

open('encoded.txt', 'wb').write(encoded)