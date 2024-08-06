'''
https://stackoverflow.com/questions/50608010/how-to-verify-a-signed-file-in-python

padding.PKCS1v15() for X.509
'''


import base64
import codecs
import cryptography.exceptions
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key
# from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates, load_pkcs12
from iot_service.utils import Utils
from common_libs import environment

_env = environment()

def validate_signature(pub_key_name, data, signature):

    # Load the public key.
    try:
        key_data = Utils.get_secret(pub_key_name).encode()
        # print('Pub Data', key_data)
        public_key = load_pem_public_key(key_data, default_backend())
    except Exception as err:
        print('Error when trying to validate signature', err)
        raise

    # # Load the public key.
    # try:
    #     with open(_env.certs_path(pub_key_name), 'rb') as f:
    #         key_data = f.read()
    #         # print('Pub Data', key_data)
    #         public_key = load_pem_public_key(key_data, default_backend())
    # except FileNotFoundError as err:
    #     raise

    # if public_key_1 != public_key:
    #     print(f"BT env_pub.pem keys not equal!")

    try:
        public_key.verify(
            bytes(signature),
            bytes(data),
            padding.PKCS1v15(),
            # padding.PSS(
            #     mgf = padding.MGF1(hashes.SHA256()),
            #     salt_length = padding.PSS.MAX_LENGTH,
            # ),
            hashes.SHA256()
        )
        return False
    except cryptography.exceptions.InvalidSignature as e:
        print('ERROR: Payload and/or signature files failed verification!')
        return True


def generate_signature(private_key_path, data):
    # Load the private key.
    with open(private_key_path, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password = 'Winn23'.encode('utf-8'),
            backend = default_backend(),
        )

    # # Load the contents of the file to be signed.
    # with open('payload.dat', 'rb') as f:
    #     payload = f.read()

    # Sign the payload file.
    signature = base64.b64encode(
        private_key.sign(
            data,
            padding.PKCS1v15(),
            # padding.PSS(
            #     mgf = padding.MGF1(hashes.SHA256()),
            #     salt_length = padding.PSS.MAX_LENGTH,
            # ),
            hashes.SHA256(),
        )
    )
    return signature
    # with open('signature.sig', 'wb') as f:
    #     f.write(signature)


def _decodeSecurityRequest(data: bytes, header: bytes):
        '''
            https://dev.azure.com/WGO-Web-Development/Owners%20App/_wiki/wikis/Owners-App.wiki/549/BLE-Messages
        '''
        method = data[0]
        print('Method', method)

        # 0x0A - fastforward
        # 0x00 - initial connection
        # 0x0B - farfield
        if method not in (0x0A, 0x00, 0x0B):
            raise ValueError(f'Method: {method} not supported')

        if method == 0x0B:
            # Proof token request
            mobile_device_id = data[1:16]
            return {
                'method': method,
                'mobileId': mobile_device_id,
            }
        else:
            cert_length = (data[2] << 8) + data[1]
            print('Cert Length', cert_length)

            cert_body = data[3:]

            # TODO: Suspended for further testing
            # if len(cert_body) != cert_length:
            #     raise IndexError(f'Received different length body, expected {cert_length},got {len(cert_body)}')

            print('Cert Body', cert_body)

            cert = _decode_cert_body(cert_body)
            print('Cert', cert)

            return {
                'method': method,
                'certificateLength': cert_length,
                'certificate': cert
            }


def _decode_cert_body(data: bytes):
    '''
    0-7 Exp Date
    8-23 Mobile Device ID
    24-47 Vehicle ID
    48-X Mobile Pub Key
    X-N Signature'''

    exp_date = data[0:8]
    exp_date = int.from_bytes(bytes(exp_date), 'little')

    mobile_device_id = data[8:24]
    mobile_device_id = ''.join([f'{y:02X}' for y in mobile_device_id])

    device_id = data[24:48]
    try:
        print(bytes(device_id).decode('utf-8'))
    except Exception as err:
        print('error', err
              )
    device_id = ''.join([f'{y:02X}' for y in device_id])

    mobile_pub_key = data[48:80]
    mobile_pub_key = ''.join([f'{y:02X}' for y in mobile_pub_key])

    signature = data[80:]
    signature = ''.join([f'{y:02X}' for y in signature])

    return {
        'expDate': exp_date,
        'mobileDeviceId': mobile_device_id,
        'deviceId': device_id,
        'mobilePubKey': mobile_pub_key,
        'signature': signature,
        'raw_cert': data[0:80],
        'raw_signature': data[80:]
    }


if __name__ == '__main__':
    # x = {'expDate': 1677886261, 'mobileDeviceId': 'C7DCAE8A6B7A444BBF7677EC8C2BAA9D', 'deviceId': '46004F004F002D2D2D2D2D424547494E2052534120505542', 'mobilePubKey': '4C4943204B45592D2D2D2D2D0A4D45674351514374326B2F7356474A316D347A', 'signature': '6B654F464A5A2B4B5A446E39587A4F74777259595757444E2F48433767774541774F63356F387A6E745543642F0A33494C314478756D2B5742566C725A655572363274553750536B745841674D424141453D0A2D2D2D2D2D454E4420525341205055424C4943204B45592D2D2D2D2D0A49AD75FB76E33A5D70B61701C98D11F4654A80C41C5A9BD707C02B2587F86B7336065505E1A436217F4355A0F1E5BC9022BD966AA6CA39B59ABDA1C3DD8DE6FACE06A9C4420D335E7A13B37C15438F1B700588B8F3CD42ED55A9F77586BC03145BCEF45E1A09D6F8F3D42A96095EC27AEF3FDA905944C95E91032E1ECBE4D54BB2CA9ADA34DFDD0D7D5EFF91CE1E44302A537406B3537B3113D596E442350D3CC084AB4D2EEDFAC9070EB2A64DCD86A95370DB1CE98053E45C7479DA04EFB3B04C1EDF5825C04742450F8446E17CD9AE23CEE1864AE6D0ECA006C2EBFB2BD172C7DDE3E5A364832199C8216049A0907B524FF78B0AE97530B68B4CD23FBECE68537E3351CE063D79C0894247E4F968AABC8A4C7BF93599040DA61D34F501D1CE982A85D0BADBE021CE868235C1BA8064F409405260CFBFEF04A0E6B75492A4CAB019F9A44CA226B64ACF99DAB21A839A3EB6CBE2B3BA37CAC06B90FFC3DFDBBF21E4E6A97912C86E3900519796A06E4942CDE4E20124283A3EF6CEE05A977DBC1B17BC310026D2AC01099E85699AFA51D169FFF9E4348C0522638F68838805A89464022EAF3D29B41915C65C422131CEF3C22B9F0F4519A543452DDF3F9AB617673DE06D048FE2331645DB3E0DF4F759CCB99B66BB76AA2B75B016B5BB8D9B3706B2BA25D6349181094A7F789B621D40F6A45210DE3D2BA13D0A58F5080B7FED0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000', 'raw_cert': [53, 131, 2, 100, 0, 0, 0, 0, 199, 220, 174, 138, 107, 122, 68, 75, 191, 118, 119, 236, 140, 43, 170, 157, 70, 0, 79, 0, 79, 0, 45, 45, 45, 45, 45, 66, 69, 71, 73, 78, 32, 82, 83, 65, 32, 80, 85, 66, 76, 73, 67, 32, 75, 69, 89, 45, 45, 45, 45, 45, 10, 77, 69, 103, 67, 81, 81, 67, 116, 50, 107, 47, 115, 86, 71, 74, 49, 109, 52, 122], 'raw_signature': [107, 101, 79, 70, 74, 90, 43, 75, 90, 68, 110, 57, 88, 122, 79, 116, 119, 114, 89, 89, 87, 87, 68, 78, 47, 72, 67, 55, 103, 119, 69, 65, 119, 79, 99, 53, 111, 56, 122, 110, 116, 85, 67, 100, 47, 10, 51, 73, 76, 49, 68, 120, 117, 109, 43, 87, 66, 86, 108, 114, 90, 101, 85, 114, 54, 50, 116, 85, 55, 80, 83, 107, 116, 88, 65, 103, 77, 66, 65, 65, 69, 61, 10, 45, 45, 45, 45, 45, 69, 78, 68, 32, 82, 83, 65, 32, 80, 85, 66, 76, 73, 67, 32, 75, 69, 89, 45, 45, 45, 45, 45, 10, 73, 173, 117, 251, 118, 227, 58, 93, 112, 182, 23, 1, 201, 141, 17, 244, 101, 74, 128, 196, 28, 90, 155, 215, 7, 192, 43, 37, 135, 248, 107, 115, 54, 6, 85, 5, 225, 164, 54, 33, 127, 67, 85, 160, 241, 229, 188, 144, 34, 189, 150, 106, 166, 202, 57, 181, 154, 189, 161, 195, 221, 141, 230, 250, 206, 6, 169, 196, 66, 13, 51, 94, 122, 19, 179, 124, 21, 67, 143, 27, 112, 5, 136, 184, 243, 205, 66, 237, 85, 169, 247, 117, 134, 188, 3, 20, 91, 206, 244, 94, 26, 9, 214, 248, 243, 212, 42, 150, 9, 94, 194, 122, 239, 63, 218, 144, 89, 68, 201, 94, 145, 3, 46, 30, 203, 228, 213, 75, 178, 202, 154, 218, 52, 223, 221, 13, 125, 94, 255, 145, 206, 30, 68, 48, 42, 83, 116, 6, 179, 83, 123, 49, 19, 213, 150, 228, 66, 53, 13, 60, 192, 132, 171, 77, 46, 237, 250, 201, 7, 14, 178, 166, 77, 205, 134, 169, 83, 112, 219, 28, 233, 128, 83, 228, 92, 116, 121, 218, 4, 239, 179, 176, 76, 30, 223, 88, 37, 192, 71, 66, 69, 15, 132, 70, 225, 124, 217, 174, 35, 206, 225, 134, 74, 230, 208, 236, 160, 6, 194, 235, 251, 43, 209, 114, 199, 221, 227, 229, 163, 100, 131, 33, 153, 200, 33, 96, 73, 160, 144, 123, 82, 79, 247, 139, 10, 233, 117, 48, 182, 139, 76, 210, 63, 190, 206, 104, 83, 126, 51, 81, 206, 6, 61, 121, 192, 137, 66, 71, 228, 249, 104, 170, 188, 138, 76, 123, 249, 53, 153, 4, 13, 166, 29, 52, 245, 1, 209, 206, 152, 42, 133, 208, 186, 219, 224, 33, 206, 134, 130, 53, 193, 186, 128, 100, 244, 9, 64, 82, 96, 207, 191, 239, 4, 160, 230, 183, 84, 146, 164, 202, 176, 25, 249, 164, 76, 162, 38, 182, 74, 207, 153, 218, 178, 26, 131, 154, 62, 182, 203, 226, 179, 186, 55, 202, 192, 107, 144, 255, 195, 223, 219, 191, 33, 228, 230, 169, 121, 18, 200, 110, 57, 0, 81, 151, 150, 160, 110, 73, 66, 205, 228, 226, 1, 36, 40, 58, 62, 246, 206, 224, 90, 151, 125, 188, 27, 23, 188, 49, 0, 38, 210, 172, 1, 9, 158, 133, 105, 154, 250, 81, 209, 105, 255, 249, 228, 52, 140, 5, 34, 99, 143, 104, 131, 136, 5, 168, 148, 100, 2, 46, 175, 61, 41, 180, 25, 21, 198, 92, 66, 33, 49, 206, 243, 194, 43, 159, 15, 69, 25, 165, 67, 69, 45, 223, 63, 154, 182, 23, 103, 61, 224, 109, 4, 143, 226, 51, 22, 69, 219, 62, 13, 244, 247, 89, 204, 185, 155, 102, 187, 118, 170, 43, 117, 176, 22, 181, 187, 141, 155, 55, 6, 178, 186, 37, 214, 52, 145, 129, 9, 74, 127, 120, 155, 98, 29, 64, 246, 164, 82, 16, 222, 61, 43, 161, 61, 10, 88, 245, 8, 11, 127, 237, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
    # pub_key_path = '/Users/dom/Documents/1_Projects/1_Winnebago/2_Dev/storage/certs/1054042BB005-0000.chain.pem'
    # pub_key_path = '/Users/dom/Documents/1_Projects/1_Winnebago/2_Dev/storage/certs/env_pub.pem'
    pub_key_name = "env_pub.pem"

    data = '0a50026d48286500000000f1e2fcb60a8a1d4a996072633c6e7dc33130353430343252503030312d303030300000000000000010d65a974a21cba6c4121dfbde0213dbf1190ffa96bd57db2bdba4820578521e2f84355ce7359eef77bcbfd8fbff23ca23039353582f7a1284dde2d01e33d1c1aa52a6c9cfa2ac358072242cd7b925142455883ebf967efaf7aa63f5432b38205955693ad3f52b816d3d0ca3a6a2a33fc2227f920a9a6d15e529c62a84e2d4ea72901d6548aca0516ba661a59a4691833710d5094132fea331a103881449d6638a02ebfc665e1509da903cf3369655bca3bb6b16d28b0aba3de1a4507ae036fac42047f1b9048ff47ee7fd8de8ef52dfbf0fa8cace8afc8098554551b4d8939e00bf73a5e1c2f175dbfe18393e3ce74ef12abd3f8598ce1b33f8b7bf3ece37169187967d67e351c3b3d0381885fd1981069a6385ef266d95c159d2d79af4c0162d9d01c833c1d7595b2cd87ab611ebd4b2cc286254f8d3f3f09a618ce7a689f1be0368fa79d9c3a6d0754cc4b58e7fa74efecd29043397f18c4476e4c0e8be69280b5fdd0a9343799762fd5a36db500bcf2237bae5ccd3749955084f2a3f8c5b3ae1adf76ae1fe67c854b10b5b1d418edd15ec49c872599254c111796e03e2ee32b94d8425eb414cbe1623f9b0ab5d10d996101da7b71c2e8869a7037c747f1c325f31b7afb789df1fe434d808b2b5b55ff675153584c69d74b233f0c07d467ff202108d94fbc936b37359e971e1163cf36fc290dfa80738007eef64579dea09fdf1f21f279ee31749f0285fcfc163ac331375271212c9665b50ba0ea9d83c05'
    data = bytes.fromhex(data)

    request = _decodeSecurityRequest(data, header=[])
    print(request)

    returned_sig = validate_signature(
        pub_key_name,
        request['certificate'].get('raw_cert'),
        request['certificate'].get('raw_signature')
    )
    print(returned_sig)

    # # returned_sig = validate_signature(private_key_path, data, signature)
