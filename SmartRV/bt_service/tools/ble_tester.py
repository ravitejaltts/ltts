'''Wraps around GATTTOOL to issue all known commands.'''

import subprocess
import sys


try:
    mac = sys.argv[1]
except IndexError:
    mac = '44:01:BB:E0:83:83'

cmd = 'sudo gatttool -b {mac} --characteristics'

result = subprocess.run(cmd.format(mac=mac), shell=True, capture_output=True)
print(result)

stdout = result.stdout.decode('utf-8')
results = {}

for line in stdout.split('\n'):
    print(line)
    if not line.strip():
        continue

    values = line.split(',')
    values = [x.strip() for x in values]

    result = {}

    for value in values:
        key, val = value.split(' = ')
        print('\t', key, val)
        result[key] = val

    uuid = result.get('uuid')
    results[uuid] = result

print(results)

SEC_REQ_UUID = '46829a01-bc2a-48bc-84af-ba68fc506b6c'
SEC_RES_UUID = '46829a02-bc2a-48bc-84af-ba68fc506b6c'
req_char = results.get(SEC_REQ_UUID)
res_char = results.get(SEC_RES_UUID)

if res_char is None:
    raise KeyError(f'Cannot find UUID: {SEC_RES_UUID}')

handle = res_char.get('char value handle')
if handle is None:
    raise ValueError(f'Cannot find handle')
else:
    handle = int(handle, 16) + 1
 
cmd = 'sudo gatttool -b {mac} --char-write-req -a {handle} -n {value} --listen'.format(mac=mac, handle=handle, value='0100')
sec_notifications = subprocess.Popen(cmd.format(mac=mac), shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
print(sec_notifications)


if req_char is None:
    raise KeyError(f'Cannot find UUID: {SEC_REQ_UUID}')


handle = req_char.get('char value handle')
if handle is None:
    raise ValueError(f'Cannot find handle')
value = '0001FFFF0A5A02FF35C063000000009D2EF802D44C23439F643F5E3F123FAC3100350038003300350034003200320032003300350030002D0030003000300030000000000000000000000000000000000000000000000000000000000000000000717BBCCD9693FBD01BF4B7F983C03B157D0B9711F26C7E17CF2DA2E848C1D1D903E17C3EF83FD77B085A3BECC62C1F889BE5F330123D08E303A308E6296C05A29266EC6E0DA1CD1A21B37DF7FE010969E1415473432282EC7159F4D3B5115986EFEF523F960C5F1C42BCFD48D4A2B6321AB9850B7B9524020166828B24656067FF45E591542D5F0CD21170046F2B48D5DB40424D2ED840E10CAF1C287F79F9B5D0B65D1D736295D9144B02A3A75C68A3775088B08D47C9C2DA7F9A8785B972F8F02A229A9000D0C7C992CFA43712FEE88DB90D770981D46C3EF03B7CD28C49104486317F09E2149B4550712AD0' 
cmd = 'sudo gatttool -b {mac} --char-write-req -a {handle} -n {value}'.format(mac=mac, handle=handle, value=value)
result = subprocess.run(cmd.format(mac=mac), shell=True, capture_output=True)
print(result)

value = '0402FFFFD233C98C8483EA567CBB582936518F34E6510A86C0497AD736A1CCEA72D4EC806F86AB5D1C6C30B7E27AF07AA36483241D0118F0EE158918C5EBD39B6718893D5D48D13EA0860E9273D1739835FF1DC87FF3AAFE30698D6CDCE579975D025A083E908AAC2E0465F759D7984B68F5C53893FCF82A1D45610CFD029FA51517F8CA1EF7428A3EB68C2D87CE1A5A1E50AA30B7920765C605996E03B282F99BDDD64BAF1A2D6CBB4DB259EBDCAB4246B5F89EF3B7D71D259B27255FF4E854402567D7E6570851508C44EE0E63F30462DCE872282C5437565E9413BE7BA921EE7D6C782F552677597518B1C32C8E6B6D5B75065950666A489F3B815F1E0461D1A3D67FDDEB76F41FC7FE1B0F565EE2898ADD7B841AA0'
cmd = 'sudo gatttool -b {mac} --char-write-req -a {handle} -n {value}'.format(mac=mac, handle=handle, value=value)
result = subprocess.run(cmd.format(mac=mac), shell=True, capture_output=True)
print(result)
