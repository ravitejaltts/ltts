import sys


messages = {}
include = []
exclude = [
    '1DFF0997',
    '1CFF0044',
    '1CFF0064',
    '19FF9CCF',
    # '1CFF0E00',
]

for line in sys.stdin:
    data = line.split('  ')
    new_updated = False
    if include and data[2] not in include:
        continue
    else:
        if data[2] in exclude:
            continue

    # print(data)
    if data[4].startswith('27 99'):
        data_key = data[2] + ''.join(data[4].split(' ')[0:4])
    elif data[2] == '1DFF0901':
        if '27 99 01' in data[4]:
            # Check what this does
            print(int(data[4].split(' ')[-1].strip(), 16) / 10)
        data_key = data[2] + data[4].split(' ')[0]
    else:
        data_key = data[2] + data[4].split(' ')[0]
    # print(data_key)
    if data_key not in messages:
        new_updated = True
    elif data[4] != messages.get(data_key):
        # print('old:', messages.get(data_key))
        new_updated = True

    if new_updated is True:
        highlight = ''
        split_data = data[4].split(' ')
        if data_key in messages:
            prev_msg_data = messages[data_key].split(' ')
            # print('Previous data', prev_msg_data)
            for i, b in enumerate(split_data):
                try:
                    prev_byte = prev_msg_data[i]
                except IndexError as err:
                    print(err, i, b)
                    break

                if b != prev_byte:
                    highlight += f'\n\tByte {i+1} >{split_data[i]}<'
                    highlight += '\n\t\t {:08b}'.format(int(split_data[i], 16))
                # else:
                #     highlight += f' {split_data[i]} '

        messages[data_key] = data[4]
        print(data, highlight)
