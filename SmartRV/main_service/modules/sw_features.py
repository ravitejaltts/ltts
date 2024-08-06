import logging
import time
from asyncio import sleep
from datetime import datetime

import httpx
import pytz

# from main_service.modules.data_helper import byte_flip
from fastapi import HTTPException, Request

from common_libs import environment
from common_libs.clients import MAIN_CLIENT
from common_libs.models.common import EventValues, RVEvents
from common_libs.models.notifications import MINIMUM_TIMEOUT, priority_to_level
from common_libs.models.notifications import NotificationPriority as priority

# from common_libs.models.common import RVEvents, EventValues
from main_service.components.inputs.pet_minder import pet_alerts
from main_service.modules.constants import (
    TEMP_UNIT_FAHRENHEIT,
    _celcius_2_fahrenheit,
)
from main_service.modules.hardware.common import HALBaseClass
from main_service.modules.logger import prefix_log
from main_service.modules.system_helper import (
    get_free_storage_mb,
    get_cpu_load,
    get_memory_usage
)

print('YMAINCLIENT', MAIN_CLIENT)
_env = environment()

wgo_logger = logging.getLogger('uvicorn.error')

HTTPX_CLIENT = httpx.AsyncClient()

# TODO: Review and delete if not purpose
INIT_SCRIPT = {}
SHUTDOWN_SCRIPT = {}


# CONSTANTS used in this hw layer

# TODO: Modify this to read from file on start
# Refer to e.g. energy for details
CONFIG_DEFAULTS = {}

# Handled wholistically in HAL Baseclase
# CODE_TO_ATTR = {}

PET_MONITOR_BATTERY_SOC_LOW_THRESHOLD = 17          # % SoC
PET_MONITOR_BATTERY_VOLTAGE_LOW_THRESHOLD = 12.8    # V
PET_MONITOR_TEMP_RANGE_HIGH_THREHOLD = 5            # F

IotBaseUrl = "http://localhost:" + str(_env.iot_service_port)

global cntw
cntw = 0


class Features(HALBaseClass):
    def __init__(self, config={}, components=[], app=None):
        HALBaseClass.__init__(self, config=config, components=components, app=app)
        for key, value in config.items():
            self.state[key] = value
        prefix_log(wgo_logger, __name__, f'Initial State: {self.state}')
        self.configBaseKey = 'features'
        self.init_components(components, self.configBaseKey)

        # if hasattr(self, 'pet_monitoring'):
        #     for instance, pm in self.pet_monitoring.items():
        #         pm.init_state()

    def update_can_state(self, system, body) -> dict:
        '''Receives direct CAN updates that belong to this layer.'''
        return super().update_can_state(body)

    def run_pet_monitoring_algorithm(self):
        '''Fired by a trigger event such as temperature, battery level etc.

        Will emit the appropriate events to create associated alerts and set flags for the UI to consider.'''
        print('[PETMINDER] Running Pet Minder Algorithm')
        # Check temperature
        thermostat = self.HAL.climate.handler.thermostat[1]
        interior_temp = thermostat.state.temp
        temp_unit = self.app.config.get('climate', {}).get(
            'TempUnitPreference',
            TEMP_UNIT_FAHRENHEIT
        )
        pet_mon = self.pet_monitoring[1]
        pet_mon_events = []

        if pet_mon.state.enabled == EventValues.OFF:
            # Disable all alerts
            print('[PETMINDER] Disabling all alerts as pet minder is off')
            for alert in (
                        RVEvents.PET_MONITOR_BATTERY_LOW,
                        RVEvents.PET_MONITOR_TEMP_HIGH,
                        RVEvents.PET_MONITOR_TEMP_LOW):

                self.event_logger.add_event(
                    alert,
                    1,                  # Petminder has a single instance
                    EventValues.OFF     # Turn off
                )

            pet_mon.state.alerts = pet_mon_events
            return pet_mon.state

        if interior_temp is not None:
            if interior_temp > pet_mon.state.maxTemp:
                # Send temp high warning
                temp_high = EventValues.ON
                temp_low = EventValues.OFF
                pet_mon_events.append(
                    RVEvents.PET_MONITOR_TEMP_HIGH
                )
            elif interior_temp is not None and interior_temp < pet_mon.state.minTemp:
                # Send temp low warning
                temp_high = EventValues.OFF
                temp_low = EventValues.ON
                pet_mon_events.append(
                    RVEvents.PET_MONITOR_TEMP_LOW
                )
            else:
                temp_high = EventValues.OFF
                temp_low = EventValues.OFF

            self.event_logger.add_event(
                RVEvents.PET_MONITOR_TEMP_HIGH,
                1,
                temp_high,
            )

            self.event_logger.add_event(
                RVEvents.PET_MONITOR_TEMP_LOW,
                1,
                temp_low,
            )

            if temp_unit == 'F':
                temp = _celcius_2_fahrenheit(interior_temp)
                temp_repr = f'{temp:.0f}°{temp_unit}'
            else:
                temp_repr = f'{interior_temp:.1f}°{temp_unit}'
        else:
            temp_repr = 'TEMP ERROR'
            temp_high = EventValues.OFF
            temp_low = EventValues.OFF

        # Check battery level
        battery = self.HAL.energy.handler.battery_management[1]
        # TODO: Yes, we need standard handling for all missing components reading
        # TODO: Should we handle missing voltages here or somewhere else ?
        # TODO: Should the default for bm values be None
        if battery.state.soc is not None:
            soc_low = battery.state.soc < PET_MONITOR_BATTERY_SOC_LOW_THRESHOLD
        else:
            soc_low = EventValues.OFF

        if battery.state.vltg is not None:
            voltage_low = battery.state.vltg < PET_MONITOR_BATTERY_VOLTAGE_LOW_THRESHOLD
        else:
            voltage_low = EventValues.OFF

        if soc_low or voltage_low:
            battery_low = EventValues.ON
            pet_mon_events.append(
                RVEvents.PET_MONITOR_BATTERY_LOW
            )
        else:
            battery_low = EventValues.OFF

        self.event_logger.add_event(
            RVEvents.PET_MONITOR_BATTERY_LOW,
            1,
            battery_low,
        )

        # Check if any actions need to be recommended
        petmon_actions = None

        # Update the messaging to show for pet monitoring
        # TODO: Move this to UI layer to assemble maybe ?
        level = priority_to_level(priority.Good)
        pet_mon_title = 'Systems Are Good'
        pet_mon_subtitle = f'Inside temp is within range: {temp_repr}'
        pet_mon_body = 'Have a Great Day !'

        pet_body_array = []

        if interior_temp is None:
            pet_alert_items = pet_alerts.get('PM2', {})
            # TODO: need to match pet minder requirements sevirity into alert requirments priority
            level = priority_to_level(priority.Pet_Minder_Warning)
            pet_mon_title = pet_alert_items.get('Headline', 'Temperature Unknown')
            pet_mon_subtitle = pet_alert_items.get('Temp Status', 'Inside temp: {temp}').format(temp=temp_repr)
            pet_mon_body = pet_alert_items.get('Short Description', 'Pet Minder cannot monitor interior temp.')
            pet_body_array.append(pet_mon_body)
        else:
            if battery_low == EventValues.ON:
                pet_alert_items = pet_alerts.get('PM25', {})
                level = priority_to_level(priority.Pet_Minder_Warning)
                pet_mon_title = pet_mon_title = pet_alert_items.get('Headline', 'Battery is Critically Low')
                pet_mon_body = pet_alert_items.get('Short Description', 'Your RV battery will run out soon.')
                pet_body_array.append(pet_mon_body)

            if temp_high == EventValues.ON:
                level = priority_to_level(priority.Pet_Minder_Warning)
                if thermostat.state.setMode not in (EventValues.AUTO, EventValues.COOL):
                    # Cooling not ON
                    pet_alert_items = pet_alerts.get('PM10', {})
                else:
                    # TODO: add in other pet requirments for AC errors
                    # This section PM14 is AC can't keep up - too severe
                    pet_alert_items = pet_alerts.get('PM14', {})

                pet_mon_title = pet_alert_items.get('Headline', 'RV Temp Above Pet Comfort')
                pet_mon_subtitle = pet_alert_items.get('Temp Status', 'Inside temp is outside range: {temp}').format(temp=temp_repr)
                pet_mon_body = pet_alert_items.get('Short Description', "Please consider turning the air conditioning on in your coach.")
                pet_body_array.append(pet_mon_body)

            elif temp_low == EventValues.ON:
                level = priority_to_level(priority.Pet_Minder_Warning)
                if thermostat.state.setMode not in (EventValues.AUTO, EventValues.HEAT):
                    # Heat not ON
                    pet_alert_items = pet_alerts.get('PM4', {})
                else:
                    # TODO: add in other pet requirments for Furnace errors
                    # This section PM8 is heat can't keep up
                    pet_alert_items = pet_alerts.get('PM8', {})

                pet_mon_title = pet_alert_items.get('Headline', 'RV Temp Below Pet Comfort')
                pet_mon_subtitle = pet_alert_items.get('Temp Status', 'Inside temp is outside range: {temp}').format(temp=temp_repr)
                pet_mon_body = pet_alert_items.get('Short Description', "Please consider turning the heat on in your coach.")
                pet_body_array.append(pet_mon_body)

        if len(pet_body_array) > 1:
            level = priority_to_level(priority.Pet_Minder_Critical)    # Any two alerts make it critical
            pet_mon_body = pet_body_array

        self.app.config['features']['petmonitoring'] = {
            'title': pet_mon_title,
            'subtitle': pet_mon_subtitle,
            'body': pet_mon_body,
            'level': level,
            'footer': {
                'actions': petmon_actions
            }
        }

        pet_mon.state.alerts = pet_mon_events

        pet_mon.update_state()  # Fire events and IOT changes

        print(
            '[PETMINDER] Updated Pet Mon state',
            self.app.config['features']['petmonitoring'],
            pet_mon.state,
            battery_low,
            temp_high,
            temp_low
        )

    @staticmethod
    async def report_all_events_task(app):
        # TODO: See where making this awaitable makes sense
        app.updateNow.increment()
        app.hal.updateStates()

    @staticmethod
    async def check_gps_task(hal):
        '''Get GPS from Cradlepoint or other connectivity device that is supported by hw_connectivity.'''
        global cntw
        cntw += 1
        print(f"[check_gps_task] Checking Location Service! {cntw} {datetime.now()}")

        try:
            # TODO: Get optin from component and pass in rather than discovery inside the connectivity
            optin = hal.vehicle.handler.vehicle[2].state.usrOptIn
            gps_data = await hal.connectivity.handler.get_sys_gps(
                {'usrOptIn': optin}
            )
            print('[check_gps_task] Result of get_sys_gps', gps_data)
        except Exception as err:
            print('Error executing check_gps_task', err)
            gps_data = None

        vehicle_loc = None

        if hasattr(hal.vehicle.handler, 'vehicle'):
            LOCATION_ID = 2
            try:
                vehicle_loc = hal.vehicle.handler.vehicle[LOCATION_ID]
            except KeyError as err:
                print('check_gps_task:', err)
                vehicle_loc = None

            if vehicle_loc.state.usrOptIn is False:
                # Don't complete this store
                return

            if vehicle_loc is not None and gps_data is not None:
                new_state = {
                    'pos': gps_data['position']
                }

                vehicle_loc.set_state(new_state)
        else:
            print('[check_gps_task] Vehicle Location Instance not load')

        if vehicle_loc:
            # TODO: Replace this with GPS component fetch loc and store
            # store if difference > some lat lon fraction amount 60 miles from default wx
            if vehicle_loc.state.pos == "NA":
                # hal.vehicle.handler.vehicle[2].state.pos = "30.651086318844573, -89.89650863720253"  # LA for today's storm alerts
                # vehicle_loc.state.pos = "37.77056, -122.42694"  # San Fran
                # hal.vehicle.handler.vehicle[2].state.pos = "28.11593482910937, -82.64615585049584"  # 12716 Silver Dollar Dr, Odessa, FL 33556
                # hal.vehicle.handler.vehicle[2].state.pos = "37.76221937383994, -104.94294637504572"  # Colorado - for winter alerts
                if hal.app.config.get('settings', {}).get('debugEnabled') is True:
                    # Set Test Location Approximate Winnebago in FC
                    vehicle_loc.state.pos = "43.2537, -93.6369"
                    # vehicle_loc.state.pos = "42.3722, -83.5408"  # Test case for Detroit
                    # vehicle_loc.state.pos = "34.68, -90.35" # checking Memphis Heat alert - June 2024
                    # ehicle_loc.state.pos = "41.31, -85.06" # checking Northern Indiana alert - June 2024
                    # vehicle_loc.state.pos = "42.20597, -121.13806" # test Medford Oregon - June 2024
                    # vehicle_loc.state.pos = "41.37, -91.15" #  Quad cities test June 2024
            else:
                print("[check_gps_task] Pos:", vehicle_loc.state.pos)

            vehicle_loc.update_state()
        return {"Pos": vehicle_loc.state.pos}

    @staticmethod
    async def register_for_weather_task(app):
        '''This will set our location to the platform for weather pushed alerts.'''
        global cntw
        cntw += 1
        gps_opt_in = app.hal.vehicle.handler.vehicle[2].state.usrOptIn
        if gps_opt_in is False:
            print(f"Register Weather NO - user is opting out of location service. {datetime.now()}")
            return

        print(f"Register Weather location with the platform! {cntw} {datetime.now()}", flush=True)
        # return #TODO: Need a real GPS for this

        if app.hal.vehicle.handler.vehicle[2].state.pos != "NA":
            try:
                # apiResponse = requests.put(
                #     IotBaseUrl + "/weather",
                #     timeout=30,  # This runs in the long schedule task and
                #     # will wait for platform slow response
                # )
                apiResponse = await HTTPX_CLIENT.put(
                    IotBaseUrl + "/weather",
                    timeout=0.5,
                )
                resp = apiResponse.json()
                # resp = json.loads(apiResponse.text)
                print(f"Weather Alert Register: {resp}")
            except Exception as err:
                print("Weather: check iot err:", err)
        else:
            print("Weather: Why no location yet?")

    async def check_tcu_information(self, counter=0):
        # TODO: Should we reschedule this if it fails to report to IoT
        try:
            modem = await self.HAL.connectivity.handler.get_modem_info()
        except Exception as err:
            print('[CONNECTIVITY] Error retrieving TCU data', err)
            # TODO: Should we retry, depends if the login failed or we had a timeout
            raise

        print('[CONNECTIVITY] MODEM DATA', modem)
        stored_info = self.app.get_config('connectivity.info')
        if stored_info is None:
            # Need to update
            self.app.save_config('connectivity.info', modem)
            stored_info = self.app.get_config('connectivity.info')

        for key, value in modem.items():
            print('[MODEM]', key, value)

        print('[CONNECTIVITY] APP Stored Information', stored_info)

        self.state['modem'] = modem

        network = self.HAL.connectivity.handler.network[1]
        network.set_state({
            'tcuId': str(modem.get('TCU_ID')),
            'imei1': str(modem.get('IMEI1')),
            'iccid1': str(modem.get('ICCID1')),
            'imei2': str(modem.get('IMEI2')),
            'iccid2': str(modem.get('ICCID2'))
        })

        # Inform IoT
        try:
            apiResponse = await HTTPX_CLIENT.put(
                IotBaseUrl + "/tcu_data",
                timeout=5,
                json=modem
            )
            resp = apiResponse.json()
            # resp = json.loads(apiResponse.text)
            print(f"TCU Data Updated: {resp}")
        except Exception as err:
            print("TCU Data: IoT Error check iot err:", err)
            counter += 1
            if counter >= 3:
                print("FAILING out of trying to update IoT", err)
                return
            else:
                await sleep(5)
                return await self.check_tcu_information(counter=counter)

        return self.state['modem']

    async def check_connectivity(self):
        # modem = await self.HAL.connectivity.handler.get_modem_info()
        print('[CONNECTIVITY] Data Check', 'Not implemented')
        return

    async def periodic_can_requests(self):
        '''Requests to queue periodically.'''
        # Request Awning Statuse
        # cansend can0 18EA8F44#BBFF0101FF - DC_Dimmer_status
        # cansend can0 18EABF44#F3FE0101FF - for awning status (edited)
        self.HAL.app.can_sender.can_send_raw(
            '18EA8F44',
            'BBFF0101FF'
        )
        # self.HAL.app.can_sender.can_send_raw(
        #     '18EABF44',
        #     'F3FE0101FF'
        # )
        # '''
        #     For below:
        #     this is for prop tm-620 configuration command to quarry state with prop_tm620_config_command.
        #     - the pgn is composed of 0XEf__ __ being the source address of the tm-620. this will not work from my testing to use FF as a catch all.
        #     - This is to select the tm 620 and in current state since source address is dynamic
        #     decoding and sending will not work if the source address would change unfortunately to be noted.
        #     - after that in the context of the message it is required to send 32 hex in byte 0 to receive the quarry; after that we are sending ignore to everything else.
        #     - we are looking at receiving 0XEF4464 in return for prop_tm620_config_status
        # '''
        self.HAL.app.can_sender.can_send_raw(
            '18EF6444',
            '32FFFFFFFFFFFFFF'
        )

    async def periodic_system_overview(self):
        '''Request system overview.'''
        SYS_OVERVIEW_INSTANCE = 3
        diagnostics = self.diagnostics[SYS_OVERVIEW_INSTANCE]

        print('CREATING STATE for Diagnostics')

        # Read cpu load
        cpu_load = get_cpu_load()
        memory = get_memory_usage()[0]
        user_storage = get_free_storage_mb('/storage')[0]
        system_storage = get_free_storage_mb('/')[0]

        new_state = {
            'cpuLoad': cpu_load,
            'memory': memory,
            'userStorage': user_storage,
            'systemStorage': system_storage,
            'updateTime': time.time()
        }

        print('SETTING STATE for Diagnostics', new_state)

        diagnostics.set_state(new_state)

        return diagnostics.state

    @staticmethod
    async def check_weather_task(app):
        global cntw
        cntw += 1
        print(f"\nChecking Weather Service task! {cntw} {datetime.now()}\n")
        # The following code requests the weather - now it is returned separately
        try:
            # apiResponse = requests.get(
            #     IotBaseUrl + "/weather",
            #     timeout=MINIMUM_TIMEOUT,  # Second timeout
            # )
            apiResponse = await HTTPX_CLIENT.get(
                IotBaseUrl + "/weather",
                timeout=MINIMUM_TIMEOUT,  # Second timeout
            )
            if apiResponse.status_code == 200:
                print(apiResponse.json())
            else:
                print(f"/weather 2 reported: {apiResponse.status_code}")
        except Exception as err:
            print(f"/weather R3 reported: {err}")

    @staticmethod
    async def receive_and_process_weather(request: Request, data):
        global cntw
        cntw += 1
        print(f"\n Weather Service task reporting back! {cntw} {datetime.now()}\n")
        try:
            wx_alerts = data.get("alerts", [])
            print(f"/weather alerts reported: {wx_alerts}")
            if wx_alerts != []:
                try:
                    weather = request.app.hal.features.handler.weather[1]
                except KeyError as err:
                    print("receive_and_process_weather: ", err)
                    raise HTTPException(404, {'msg': f'Cannot find weather instance {1}'})

                print("Processing weather alerts.")
                for wx_condition in wx_alerts:
                    weather.input_alert(request.app, wx_condition)
            else:
                print(f"/weather reported NO alerts!")
            result = True
        except Exception as err:
            print(f"/weather 3 reported: {err}")

        if result is False:
            # reschedule ourselves  or set a test to report the failure?
            print("/weather 4 Failed - should we reschedule or report")
            return

    @staticmethod
    async def check_sunset(app):
        print('[SUNSET] Checker if sunset / sunrise requires dark/light mode change')
        preferred_timezone = app.config.get('timezone').get("TimeZonePreference")
        if app.config.get('settings', {}).get('AutoScreenModeSunset') == EventValues.ON:
            tz = pytz.timezone(preferred_timezone)
            # current_time_preferred_timezone = datetime.now(tz).strftime('%I:%M %p')
            current_zone_time = datetime.now(tz)

            minutes_in_current_day = current_zone_time.hour * 60 + current_zone_time.minute
            # 390 = 6:30 / 1110 = 18:30
            if minutes_in_current_day > 390 and minutes_in_current_day < 1110:
                # Light Mode
                app.config['settings']['UIScreenMode'] = 'LIGHT'
                print('Setting LIGHT MODE')
            else:
                # Dark Mode
                app.config['settings']['UIScreenMode'] = 'DARK'
                print('Setting DARK MODE')

        else:
            print('[SUNSET] Disabled')

        return app.config['settings']['UIScreenMode']


module_init = (
    Features,
    'features_mapping',
    'components'
)

if __name__ == '__main__':
    pass
