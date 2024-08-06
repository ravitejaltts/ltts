import sys
import time
from fastapi import APIRouter,  HTTPException
from fastapi import Request, Response
import uuid
from utils import Utils, StateLog
from fastapi.responses import PlainTextResponse

from common_libs import environment
from common_libs.system.scheduled_function import ScheduledFunction
from common_libs.system.schedule_manager import ScheduledFunctionManager
from pydantic import BaseModel, validator
from iot_service.utils import Iot_Status, Utils, REMOTE_SERVER, read_file_to_string
from iot_service.platform_api import PlatformApi

_env = environment()

VIN_LENGTH = 17
VIN_INVALID = "ABCDEFG1234567890"  # The default in main should not be submitted


class VIN_Validator(BaseModel):
    vin: str

    @validator('vin')
    def check_vin_length(cls, vin):
        if vin is None:
            raise ValueError('VIN cannot be None')
        elif(len(vin) < VIN_LENGTH):
            raise ValueError('VIN too short')
        elif (len(vin) > VIN_LENGTH):
            raise ValueError('VIN too long')
        elif vin == VIN_INVALID:
            raise ValueError('VIN default invalid')
        return vin


router = APIRouter(
    prefix="",
)


@router.put("/vin")
async def put_vin(request: Request, vin: VIN_Validator):
    result = ""
    # Get new certs based on this vin
    if vin != request.app.iot_device_client.vin:
        inputvin = vin.vin
        Utils.pushLog(f"Vin change started {inputvin}")
        result = request.app.iot_device_client.vin_received(inputvin)
    else:
        if request.app.iot_device_client.iotStatus == Iot_Status.VEHICLE_RECORDS_NOT_RECEIVED:
            request.app.iot_device_client.vin = None
            inputvin = vin.vin
            Utils.pushLog(f"Vin change started {inputvin}")
            result = request.app.iot_device_client.vin_received(inputvin)
        else:
            result = f"Vin Exists {request.app.iot_device_client.vin}"

    return {"result": result}


@router.get("/vin")
async def get_vin(request: Request):
    #  Return the vin we are working with
    result = request.app.iot_device_client.vin
    if result is None:
        result = "The IOT service has not been giving a VIN yet."
    return {
        "vin": result
    }

@router.put("/tcu_data")
async def put_tcu(request: Request, tcu: dict):
    result = ""
    #
    if tcu != request.app.iot_device_client.tcu:
        Utils.pushLog(f"TCU change started {tcu}")
        result = request.app.iot_device_client.tcu_received(tcu)
    return {"result": result}


@router.get("/tcu_data")
async def get_tcu(request: Request):
    result = request.app.iot_device_client.tcu()  # function to return the data
    return result




@router.get("/far_field_token")
async def get_proof(request: Request):
    if request.app.iot_device_client.iotStatus != Iot_Status.CONNECTED:
        raise HTTPException(503, {'msg': 'IOT is not in a CONNECTED state.'})
    return {"proofToken": request.app.iot_device_client.proof_token()}


@router.get("/device_id")
async def get_device_id(request: Request):
    """return the device id assigned by the platform"""
    return {
        'device_id': request.app.iot_device_client.configParser["Device"].get("device_id","")
    }


@router.get("/latest_events")
async def get_latest_events(request: Request):
    return request.app.iot_device_client.latest_events()



@router.get("/status")
async def get_status(request: Request):
    try:
        ota_last = read_file_to_string(_env.log_file_path('ota_exit_error.txt'))
    except FileNotFoundError:
        ota_last = "Unknown"
    return { "device_id": f'{request.app.iot_device_client.configParser["Device"].get("device_id","")}',
             "status": f'{request.app.iot_device_client.iotStatus.name}',
             "msg": f'{request.app.iot_device_client.iotStatusMsg}',
             "os_version_id": request.app.iot_device_client.os_host_name,
             "software_version": f'{request.app.iot_device_client.ota_control.current}',
             "env_url": f'{request.app.iot_device_client.configParser["Device"].get("api_url","")}',
             "ota_status": f'{request.app.iot_device_client.ota_control.status.name}',
             "ota_msg": f'{request.app.iot_device_client.ota_control.status_msg}',
             "ota_last_error": ota_last,
             "iot_ver": f'{request.app.iot_device_client.file_version}',
             "serial_number": f'{request.app.iot_device_client.configParser["Device"].get("serial_number","")}',
             "model_year": f'{request.app.iot_device_client.configParser["Device"].get("model_year","")}',
             "releaseVersionCurrent": f'{request.app.iot_device_client.ota_control.current}',
             "releaseVersionWaiting": f'{request.app.iot_device_client.ota_control.waiting}',
             "releaseVersionChecked": f'{request.app.iot_device_client.ota_control.waiting_ts}'}

@router.get("/status2")
async def get_status2(request: Request):
    return { "floorPlan": f'{request.app.iot_device_client.configParser["Device"].get("floorplan","")}',
             "optionCodes": f'{request.app.iot_device_client.configParser["Device"].get("optioncodes","")}',
             "attributes": f'{request.app.iot_device_client.configParser["Device"].get("attributes","")}',
             "position": f'{request.app.iot_device_client.iot_telemetry.iot_position}',
            f"Can reach {REMOTE_SERVER}": f'{Utils.have_internet()}',
            "assigned_hub": f'{request.app.iot_device_client.configParser["Device"].get("assigned_hub","")}',
            "device_type": f'{request.app.iot_device_client.configParser["Device"].get("device_type","")}'}

@router.get("/disk_space")
async def get_disk_space(request: Request):
    return { "diskSpace": f'{Utils.get_disk_space()}'}

@router.put("/ota_start")
async def put_ota(request: Request,):
    # Let the OTA update progress
    result = request.app.iot_device_client.ota_restart()

    return result

@router.put("/iot_restart")
async def quit_iot(request: Request,):
    # Stop IOT service cleanly as possible
    result = request.app.iot_device_client.iot_restart()
    return result

@router.get("/check-cert")
async def check_cert(request: Request, name: str):
    result = Utils.disp_der_from_vault(name)
    return result

@router.get("/state-log", response_class=PlainTextResponse)
async def dump_state_log():
    return Response(content= StateLog.report(), media_type="text/plain")


@router.get("/weather")
async def get_weather(request: Request):
    """Start the process to the  weather forcast from the platform"""
    try:
        once_task = ScheduledFunction(function=PlatformApi.get_weather_forcast,
                                                        args=(request.app.iot_device_client.provisioner.api,),
                                                        wait_seconds=(2),  # once to start as one shot - wait 15 min to see if gps lock arrives
                                                        oneshot=True)

        request.app.taskScheduler.add_timed_function(once_task)
        return 200, {"Status": "Processing"}
    except Exception as err:
        Utils.pushLog(f"get_weather {err}")
        return 500, err


@router.put("/weather")
async def put_weather(request: Request):
    """post lat lng for alerts from the platform"""
    return request.app.iot_device_client.provisioner.api.post_alert_register()
