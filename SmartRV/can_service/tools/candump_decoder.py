import sys

import cantools
from pprint import pprint

db = cantools.database.load_file('rvc.dbc')

for message in db.messages:
    pprint(message)
    
    priority = int(
        (message.frame_id & 0xF8000000) >> 26
    )
    print('Priority', priority)
    dgn = hex(
        (message.frame_id & 0x03FFFF00) >> 8
    )
    print('DGN', dgn)
    
    source_address = int(
        (message.frame_id & 0x000000FF)
    )
    
    print('Source Address', source_address)
    

