import asyncio
from azure.iot.device.aio  import IoTHubDeviceClient
from azure.iot.device import X509
import json

"""
    UPDATE YOUR VARIABLES HERE
"""
public_key_file_path = "/storage/wgo/certs/1054042RP001-0000.pem"
private_key_file_path = "/storage/wgo/certs/1054042RP001-0000.key"
host_name = "iot-wgo-winnconnect-iot-hub-cus-tst.azure-devices.net"
device_id = "1054042RP001-0000"

async def main():

    x509 = X509(
        cert_file=public_key_file_path,
        key_file=private_key_file_path,
        pass_phrase="", # replace if using password
    )

    device_client = IoTHubDeviceClient.create_from_x509_certificate(
        hostname=host_name, device_id=device_id, x509=x509
    )

    reported_properties_patch = {
        'proofToken': '54321',
        'ota': {
            'path': "https://dev-apim.ownersapp.winnebago.com/api/device-types/deviceTypes/vdt/releases/latest",
            'status': 8,
            'releaseVersionCurrent': "1.0.0"
        },
        "alerts": [
            {
                "id": "my-test-asdfasdfasdfasdfasdfdsafasdasaf",
                "code": "REFRIGERATOR_OUT_OF_RANGE",
                "alertType": "status",
                "priority": "0",
                "message": "Refrigerator Temp. out of range! asdfasdfasdf",
                "active": True,
                "opened": 1683950191040,
                "dismissed": 1683950191024,
                "category": "testCategory"
            }
        ],
        "requests": [
            {
                "id": "0",
                "requested": 1692993216485,
                "completed": 1692993217493,
                "result": "success",
                "source": "platform",
                "command": {
                    "name": "APIRequest",
                    "parameters": {
                        "body": {
                            "onOff": 12
                        },
                        "method": 4,
                        "url": "/api/lighting/lz/4/state"
                    }
                }
            },
            {
                "id": "1",
                "requested": 1692993216485,
                "result": "success",
                "source": "platform",
                "command": {
                    "name": "APIRequest",
                    "parameters": {
                        "body": {
                            "onOff": 1
                        },
                        "method": 4,
                        "url": "/api/lighting/lz/4/state"
                    }
                }
            },
            {

                "id": "2",
                "requested": 1692993216485,
                "completed": 1692993217493,
                "result": "success",
                "source": "platform",
                "command": {
                    "name": "APIRequest",
                    "parameters": {
                        "body": {
                            "onOff": 1
                        },
                        "method": 4,
                        "url": "/api/lighting/lz/4/state"
                    }
                }
            }
        ]
    }

    try:
        await device_client.connect()
        await device_client.patch_twin_reported_properties(reported_properties_patch)
        result = await device_client.get_twin()
        print(json.dumps(result, indent=2))
    except:
        print("There was an error updating the reported properties of the device...")
    finally:
        await device_client.shutdown()

if __name__ == "__main__":
    asyncio.run(main())