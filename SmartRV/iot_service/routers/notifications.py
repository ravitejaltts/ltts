
import time
from fastapi import APIRouter
from fastapi import Request
from iot_service.models.telemetry_msg import AlertMsg, RequestMsg

from common_libs.models.common import LogEvent
from iot_service.utils import Utils

router = APIRouter(
    prefix="/telemetry",
    tags=[
        "Telemetry",
    ],
)

@router.put("/event")
async def put_event(request: Request, i_event: LogEvent) -> dict:
    try:
        # Utils.pushLog(f"incoming event {i_event}")
        request.app.iot_device_client.check_m2_event(i_event)
    except Exception as err:
        print("M2event err ", err)
    return {"status": "OK", "result": True}


@router.put("/alert")
async def put_alert(request: Request, i_alert: AlertMsg) -> dict:
    try:
        # print("Put alert into iot queue ", i_alert)
        request.app.iot_device_client.iot_telemetry.queue_alert(i_alert)
    except Exception as err:
        print("M2alert err ", err)
    return {"status": "OK", "result": True}


@router.put("/request")
async def put_request(request: Request, i_request: RequestMsg) -> dict:
    try:
        i_request.completed = str(int(time.time() * 1000))
        print("put request into iot queue", i_request)
        request.app.iot_device_client.iot_telemetry.queue_request(i_request)
    except Exception as err:
        print("M2request err ", err)
    return {"status": "OK", "result": True}


@router.get("/header")
async def get_header(request: Request):
    return request.app.iot_device_client.iot_telemetry.get_m1_header()


@router.get("/twin_data")
async def get_twin(request: Request):
    """return the twin data present"""
    return request.app.iot_device_client.iot_telemetry.twinData


@router.get("/new_twin_data")
async def get_new_twin(request: Request):
    """return the new twin data present"""
    return request.app.iot_device_client.iot_telemetry.twinDataNew


@router.get("/twin_data_remote")
async def get_twin(request: Request):
    """return the twin data present"""
    return request.app.iot_device_client.remoteDeviceTwin


@router.get("/alert_data")
async def get_alert(request: Request):
    """return the alert data present"""
    return request.app.iot_device_client.iot_telemetry.alertDict


@router.get("/twin_list")
async def get_twin_list(request: Request):
    """return the twin data list"""
    return request.app.iot_device_client.iot_telemetry.twinList

@router.get("/event_list")
async def get_events_list(request: Request):
    """return the iot events data list"""
    return request.app.iot_device_client.iot_telemetry.iotEventsList
