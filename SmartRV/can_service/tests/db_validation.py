from pprint import pprint
import os
import sys

import cantools


in_dir = sys.argv[1]

dbc_files = os.listdir(in_dir)
dbc_files = [
    os.path.join(in_dir, x) for x in dbc_files if os.path.splitext(x)[1] == '.dbc'
]

for filename in dbc_files:
    print('\n\n')
    print(f'Parsing {filename}')
    db = cantools.database.load_file(filename)
    print('\n')
    pprint(db.messages)
    print('\n')
    for msg in db.messages:
        pprint(msg.signals)
