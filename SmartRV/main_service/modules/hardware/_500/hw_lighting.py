# Does the light have zones ?
# Does the light have RGB capabilities
# Does the light have brightness, if yes, what is the value for 0% and 100% and in between
#
import threading
import time

from common_libs.models.common import EventValues, RVEvents
from main_service.modules.hardware.common import BaseLighting
from main_service.modules.hardware.czone.control_rv_1 import CZone
from main_service.modules.hardware.itc.itc227rgbw import CONTROLLER_ID_TO_ADDR, ITC
from main_service.modules.hardware.rvc import RVC

# Monitor the CZONE light that CZONE currently controls
# This will change when we intercept the momentary switch can messges and
# implement the fuctions for the light czone is doing


# Initialize lighting controllers used in this model
czone = CZone(cfg={"mapping": {}, "controller_id": [0x00, 0x00], "zones": {}}, load_from='hw_lighting')
itc_1 = ITC(cfg={"controller_id": 1, "zones": {}})
itc_2 = ITC(cfg={"controller_id": 2, "zones": {}})


settings = {
    "title": "Lighting System Settings",
    "configuration": None,
    "information": [
        {
            "title": "MANUFACTURER INFORMATION",
            "items": [
                {
                    "title": "Galley Light",
                    "sections": [
                        {
                            "title": None,
                            "items": [
                                {"key": "Manufacturer", "value": "ITC"},
                                {"key": "Product Model", "value": "???"},
                            ],
                        }
                    ],
                },
                {
                    "title": "Accent Light",
                    "sections": [
                        {
                            "title": None,
                            "items": [
                                {"key": "Manufacturer", "value": "ITC"},
                                {"key": "Product Model", "value": "???"},
                            ],
                        }
                    ],
                },
            ],
        }
    ],
}


ZONE_TO_BIT = {
    1: 1,
    2: 1,
    3: 1,
    4: 1,
    5: 2,
    6: 2,
    7: 2,
    8: 2,
    9: 4,
    10: 4,
    11: 4,
    12: 4,
    13: 8,
    14: 8,
    15: 8,
    16: 8,
}

DEFAULT_BRIGHTNESS = 80
DEFAULT_DIMMING = -10
MIN_LIGHTING_BRIGHTNESS = 5     # %
MAX_LIGHTING_BRIGHTNESS = 100   # %




# R has CZone
CZONE_ZONES = (31, )
RVC_ZONES = (17, )
# all TOOGLE BUT 10? - now 10 included
TOGGLED_ZONES = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17)
# TODO: Is there an awning light button ?


RGBW_DEFAULT = "#00000000"
COLOR_TEMP_DEFAULT = 5000
BRIGHTNESS_DEFAULT = 80
LED_MIN_BRIGHTNESS = 5

MASTER_DEFAULT = {
    "onOff": 0,
    "_rgb": RGBW_DEFAULT,
    # "clrTmp": 4000,
    "brt": 80
}

# DEFAULT_LIGHTS = default_light_setting()
DEFAULT_LIGHTS = [
    6,
    7,
    10,
    11,
    15,
    16
]

init_script = {
    # Should a real script go here for init
}

shutdown_script = {}

ZONE_DEFAULTS = {
    "RGBW": {"onOff": 0, "brt": 80, "_rgb": RGBW_DEFAULT, "clrTmp": 5000},
    "SIMPLE_DIM": {"onOff": 0, "brt": 100, "_rgb": RGBW_DEFAULT},
    "SIMPLE_ONOFF": {"onOff": 0},
}

def brightness_to_rgb_hex(brightness):
    """Take a percentage brightness and convert to hex color intensity between 0-255"""
    if brightness == 0:
        hex_brightness = 0
    elif brightness == 100:
        hex_brightness = 255
    else:
        hex_brightness = int(255 / 100 * brightness)

    return hex_brightness

DIMMING_TIMER_SECS = 0.7
DIMMING_CHANGE_VALUE = 5

class DimSwitchController:
    def __init__(self, lightingObj, zone_id):
        self.lock = threading.Lock()
        self.dim_direction = -1  # -1 for dimming, 1 for brightening
        self.timer = None
        self.timer_running = False
        self.timer_hit_once = False  # Track if the timer has hit at least once
        self._controller = lightingObj
        self._zone_id = zone_id
        self.pressed = False
        self.was_pressed = False

    def set_state(self, switch_pressed):
        self.was_pressed = self.pressed
        self.pressed = bool(switch_pressed)
        zone = self._controller.lighting_zone[self._zone_id]
        with self.lock:
            if switch_pressed:
                print("Switch Pressed.")
                if self.timer_running is False:
                    self.start_or_restart_timer()
                if zone.state.onOff != EventValues.ON:
                    zone.state.onOff = EventValues.ON
                    zone.set_state(zone.state.dict())
                    self.timer_hit_once = True # Fake so we don't off on release
                    # self.brightness = 100
                    print(f"Light turned on at {zone.state.brt}% brightness.")

            else:
                print("Switch Released!!!")
                self.stop_timer()
                if self.was_pressed is True:
                    if self.timer_hit_once is False:
                        zone.state.onOff = EventValues.OFF
                        zone.set_state(zone.state.dict())
                        print("Light turned off due to switch release and no timer hit.")

    def start_or_restart_timer(self):
        if self.timer_running is True:
            self.timer.cancel()  # Cancel existing timer to avoid multiple timers running
        else:
            self.timer_hit_once = False
            self.timer_running = True
        self.timer = threading.Timer(DIMMING_TIMER_SECS, self.dim_light)
        self.timer.start()
        #print("Timer started or restarted.")

    def stop_timer(self):
        if self.timer_running:
            self.timer.cancel()
            self.timer = None
            self.timer_running = False
            print("Timer stopped.")

    def dim_light(self):
        zone = self._controller.lighting_zone[self._zone_id]
        with self.lock:
            # print("Timer hit")
            self.timer_hit_once = True
            new_brightness = zone.state.brt + self.dim_direction * DIMMING_CHANGE_VALUE
            if new_brightness < MIN_LIGHTING_BRIGHTNESS or new_brightness > MAX_LIGHTING_BRIGHTNESS:
                self.dim_direction *= -1 # Change direction of dimming
                new_brightness = zone.state.brt + self.dim_direction * DIMMING_CHANGE_VALUE
            zone.state.brt = new_brightness
            print(f"adjust_brightness to {new_brightness}%")
            zone.set_state(zone.state.dict())
            self.start_or_restart_timer()  # Restart timer for continuous dimming


class Lighting(BaseLighting):
    # lighting_zones = []  # not used since transition so components
    switch_list = []

    def __init__(self, config={}, components=[], app=None):
        global DEFAULT_LIGHTS
        BaseLighting.__init__(self, config=config, components=components, app=None)

        # TODO: What are we doing with these attributes / variables ?
        self.configBaseKey = "lighting"

        # TODO: Get from config not in module global variable
        self.default_zones = config.get(
            "default_on_lighting_zones",
            DEFAULT_LIGHTS
        )
        # self.lighting_zones = config.get("zones", [])
        self.hw_lighting = {v['id']: v for v in config.get("zones", [])}

        for x in TOGGLED_ZONES:
            self.switch_list.append(DimSwitchController(self, x))
        # self.zones_by_id = {x.get("id"): x for x in self.lighting_zones}

        self.itc_accept_state = True
        # TODO: Try not to hard code this
        self.itc_zones_status = {
            1: {},
            2: {},
            3: {},
            4: {}
        }

        # for hmi_zone in range(1, 18):
        #     # TODO Get saved states
        #     # Default to bright and off
        #     # r = g = b = w = 0x00

        #     # hmi_zone = (zone_id -1) * 4 + 1
        #     # #print(f'>>>>> HMI Zone {hmi_zone} r {r}')

        #     #    self._update_state(hmi_zone, {'onOff': 1})  if r > 0:
        #     # else:
        #     self._update_state(hmi_zone, {"onOff": 0})
        #     self._update_state(hmi_zone, {"_rgb": RGBW_DEFAULT})
        #     self._update_state(hmi_zone, {"brt": 0x64})

        #     # hmi_zone = hmi_zone + 1

        #     # ##print(f'>>>>> HMI Zone {hmi_zone} g {g}')
        #     # if g > 0:
        #     #     self._update_state(hmi_zone, {'onOff': 1})
        #     # else:
        #     #     self._update_state(hmi_zone, {'onOff': 0})
        #     # self._update_state(hmi_zone, {'brt': 0x64})
        #     # self._update_state(hmi_zone, {'_rgb': RGBW_DEFAULT})

        #     # hmi_zone = hmi_zone + 1
        #     # ##print(f'>>>>> HMI Zone {hmi_zone} b {b}')
        #     # if b > 0:
        #     #     self._update_state(hmi_zone, {'onOff': 1})
        #     # else:
        #     #     self._update_state(hmi_zone, {'onOff': 0})
        #     # self._update_state(hmi_zone, {'brt': b})
        #     # self._update_state(hmi_zone, {'_rgb': RGBW_DEFAULT})

        #     # hmi_zone = hmi_zone + 1
        #     # ##print(f'>>>>> HMI Zone {hmi_zone} w {w}')
        #     # if w > 0:
        #     #     self._update_state(hmi_zone, {'onOff': 1})
        #     # else:
        #     #     self._update_state(hmi_zone, {'onOff': 0})
        #     # self._update_state(hmi_zone, {'brt': b})
        #     # self._update_state(hmi_zone, {'_rgb': RGBW_DEFAULT})
        # # self.savedState = load_state()
        self.HAL = None
        self.configBaseKey = "lighting"
        self.init_components(components, self.configBaseKey)

        self.rvc = RVC(cfg={})

        # Inject HW details needed from config for now
        for i, lz in self.lighting_zone.items():
            if i in self.hw_lighting:
                lz.attributes['hw'] = self.hw_lighting.get(i)
            else:
                print('Not found', i, type(i))

            # TODO: Find the right spot for this
            # lz.state.brt = 50

    def setHAL(self, hal_obj):
        czone.set_hal(hal_obj)
        self.rvc.setHAL(hal_obj)
        super().setHAL(hal_obj)

    # def load_state(self):
    #     """Read state from storage or memory or CAN bus."""
    #     state = {}
    #     for zone in self.lighting_zones:
    #         zone_id = zone.get("id")
    #         zone_type = zone.get("type")

    #         zone_default = zone.get(zone_type, ZONE_DEFAULTS[zone_type])
    #         # ##print('Zone default: ', zone_default)

    #         state[zone_id] = zone_default

    #         return state

    def _build_controller_map(self, controller_list):
        pass

    def _is_channel_restricted(self, zone_id):
        """Check if the given zone operates only a single channel of RGBW lighting."""
        zone = self.lighting_zone.get(zone_id)
        if zone is None:
            raise ValueError(f"Zone {zone_id} not supported/available")

        channel = zone.attributes.get('hw', {}).get("channel")
        if channel in ("R", "G", "B", "W"):
            return channel

        return None

    def _get_controller_id_from_zone(self, zone_id):
        if zone_id == 0:
            controller_id = "FFFF"
        else:
            try:
                controller_id = self.zones_by_id[zone_id]["controller"].cfg["controller_id"]
                controller_id = CONTROLLER_ID_TO_ADDR.get(controller_id)
                if controller_id is None:
                    raise ValueError(
                        f"Zone {zone_id} not found in zone mapping of controller"
                    )
            except:
                controller_id = "FFFF"
        return controller_id

    def _send_ctr_command(self, controller_id, zone, command, value):
        cmd = f"{controller_id}{command}{zone}{value}"
        self.HAL.app.can_sender.can_send_raw(
            '0CFC0044',
            cmd
        )

    def _init_config(self):
        #
        return
        # Get zones
        # TODO:
        config_found = False
        for i in range(10):
            index = i + 1
            key = f"{self.configBaseKey}.zone.{index}"
            config_value = self.HAL.app.get_config(key)
            # #print('>>>>>> LIGHTING >>>', key, config_value)

            if config_value is not None:
                config_found = True
                # Do something with the light
                ##print(f'Config for light zone {index} {config_value}')
                self._light_switch(index, config_value)
            else:
                # set a generic default off
                self._light_switch(
                    index,
                    {
                        "onOff": 0,
                        "brt": BRIGHTNESS_DEFAULT,
                        "_rgb": RGBW_DEFAULT,
                        "clrTmp": 5000,
                    },
                )
        # Get presets handled on App level

    def _update_state(self, zone, new_state):
        print(f'[ LIGHTING 22 ] Updating zone {zone } new state {new_state}')
        if zone in self.state:
            zone_state = self.state[zone]
        else:
            zone_state = {}

        # ##print('Zone State', zone_state)

        updated_keys = []

        # Check for changes in the zone state keys
        for key, value in new_state.items():
            if key in zone_state:
                if value != zone_state.get(key):
                    updated_keys.append(key)
                    zone_state[key] = value
            else:
                zone_state[key] = value
                updated_keys.append(key)

        print('Final zone state', zone_state)

        self.state[zone] = zone_state

        print('[ LIGHTING 22b ]',self.state[zone], updated_keys)

        return updated_keys

    def get_zone(self, hmi_id):
        # Get the HMI lighting zone state
        # which when use channels is different
        return self.state[hmi_id]

    def light_status(self):
        lights_on = 0
        lights_off = 0
        lights_unknown = 0

        for zone_id, zone in self.lighting_zone.items():
            # Hidden lights shall not count towards UI
            if zone.attributes.get('hidden') is True:
                continue

            if zone.state.onOff == 1:
                lights_on += 1
            elif zone.state.onOff == 0:
                lights_off += 1
            else:
                lights_unknown += 1

        return {
            "on": lights_on,
            EventValues.OFF: lights_off,
            "na": lights_unknown
        }

    def light_status_new(self):
        lights_on_external = 0
        lights_on_internal = 0
        lights_off = 0
        lights_unknown = 0

        for zone_id, zone in self.lighting_zone.items():
            # Hidden lights shall not count towards UI
            if zone.attributes.get('hidden') is True:
                continue

            light_type = 'INTERNAL'

            if zone.attributes.get('external') is True:
                light_type = 'EXTERNAL'

            if zone.state.onOff == 1:
                lights_on_internal += 1
            elif zone.state.onOff == 0:
                lights_on_internal += 1
            else:
                lights_unknown += 1

        return {
            "on": lights_on_internal,
            "external": lights_on_external,
            EventValues.OFF: lights_off,
            "na": lights_unknown
        }

    def perform_reset(self, set_all_on=False):
        """Execute a lighting reset.

        Might be needed if lighting controllers misbehave or SW issues
        block recovery.
        """
        # Turn all non default lights off to avoid misconfiguration
        # Only applies to ITC lights as identified in their type attribute
        for zone_id, zone in self.lighting_zone.items():
            if 'ITC' in zone.attributes.get('type'):
                if zone_id not in self.default_zones:
                    self.zone_switch(zone_id, 0)

        # Open EEPROM
        self.HAL.app.can_sender.can_send_raw('0CFC0044', 'FFFF6E01FFFFFFFF')
        # Set to single color mode
        self.HAL.app.can_sender.can_send_raw('0CFC0044', 'FFFF02FF00FFFFFF')

        # Set Cycle Time
        self.HAL.app.can_sender.can_send_raw('0CFC0044', 'FFFF32C8C8C8C8FF')

        # Set lighting to white
        # "0CFC0044#FFFF01FFFFFFFF00;"
        # set brightness to 75%
        # "0CFC0044#FFFF03FF4040;"
        # Set color temp range 3000 - 9000 K / Not applicable to 500
        # "0CFC0044#FFFF3DFF0BB82328;"

        if set_all_on is True:
            for zone_id, zone in self.lighting_zone.items():
                self.zone_switch(zone_id, 1)
                self.zone_brightness(zone_id, 80)
        else:
            for zone_id, zone in self.lighting_zone.items():
                print(f'zone id {zone_id}')
                if zone_id in self.default_zones:
                    self.zone_switch(zone_id, 1)
                else:
                    print(f'zone id {zone_id}')
                    self.zone_switch(zone_id, 0)

                if zone.type not in ('simple',):
                    # Only set brightness for zones upporting it
                    self.zone_brightness(zone_id, 80)

        # Save to EEPROM
        self.HAL.app.can_sender.can_send_raw('0CFC0044', 'FFFF6E00FFFFFFFF')

    def enable_disco(self):
        """Set the unit to disco mode to test lighting reset (and for fun).

        Might be needed if lighting controllers misbehave or SW issues block
        recovery.
        """
        self.HAL.app.can_sender.can_send_raw('0CFC0044', 'FFFF07FF00')
        return

    def get_hw_info(self):
        return {}

    def get_state(self, zone=None, key=None):
        """Return state of lighting system."""
        if zone is not None:
            if key is None:
                # Return the whole zone
                # ##print('GetState', self.state)
                return self.lighting_zone.get(zone).state
            else:
                key_result = self.state.get(zone, {}).get(key)
                return key_result

        return self.state

    def get_master_light_state(self, zone_id=0):
        """Get the current values/states for the master light switch."""
        key = f"zone_{zone_id}"
        master_state = self.state.get(key, MASTER_DEFAULT)

        light_status = self.light_status()
        lights_on = light_status.get("on")
        return {"onOff": 1} if lights_on > 0 else {"onOff": 0}

    def set_master_light_state(self, new_state, zone_id=0):
        """Set the new state for master light switch."""
        key = f"zone_{zone_id}"
        self.state[key] = new_state

    def get_zones_ui(self):
        """Assemble zone config for UI response."""
        pass

    def _light_switch(self, zone_id, light_control):
        """Apply the HW specific controls needed to set the light to desired state.

        Only meant to be called from HW layer here
        Assumes that data is validated before saved to the DB"""
        zone_details = self.lighting_zone.get(zone_id)
        zone_type = zone_details.type
        zone_state = zone_details.state
        onoff_result = None
        brightness_result = None
        rgb_result = None
        color_temp_result = None

        if zone_type == "SIMPLE_ONOFF":
            onoff_result = self.zone_switch(zone_id, light_control["onOff"])
            # Check if ITC channel restricted
            if "ITC" in zone_details.get("controller_type", ""):
                # This is an ITC circuit that needs a brightness to work
                # As it is also a simple light it will be statically set to 100%
                brightness_result = self.zone_brightness(zone_id, 100)

        elif zone_type == "dimmable":
            onoff_result = self.zone_switch(zone_id, light_control.get("onOff", 0))
            zone_bright = self.zone_brightness(
                zone_id,
                light_control.get("brt"),
                # zone_state.__getattribute__("brt"),
                # BRIGHTNESS_DEFAULT,
            )
            brightness_result = brightness_to_rgb_hex(zone_bright)
            channel = self._is_channel_restricted(zone_id)
            if channel is not None:
                rgbw = zone_state.get("_rgb").replace("#", "")
                rgbw_list = ["#"]
                while rgbw:
                    rgbw_list.append(rgbw[:2])
                    rgbw = rgbw[2:]
                if light_control["onOff"] == 1:
                    if channel == "R":
                        rgbw_list[1] = "{:02X}".format(brightness_result)
                    elif channel == "G":
                        rgbw_list[2] = "{:02X}".format(brightness_result)
                    elif channel == "B":
                        rgbw_list[3] = "{:02X}".format(brightness_result)
                    elif channel == "W":
                        rgbw_list[4] = "{:02X}".format(brightness_result)
                else:
                    if channel == "R":
                        rgbw_list[1] = "00"
                    elif channel == "G":
                        rgbw_list[2] = "00"
                    elif channel == "B":
                        rgbw_list[3] = "00"
                    elif channel == "W":
                        rgbw_list[4] = "00"
                ##print(f"rgbw_list {''.join(rgbw_list)}")

                rgb_result = self.zone_rgbw(zone_id, "".join(rgbw_list))
                # self._update_state(zone_id, {'_rgb':''.join(rgbw_list)})
            else:
                print(f"Zone_id {zone_id} not reporting as using channel")

        result = {
            "onOff": onoff_result,
            "brt": brightness_result,
            "_rgb": rgb_result,
            "clrTmp": color_temp_result,
        }
        return result

    def toggle_zone_switch(self, zone_id, on_off):
        try:
            switch = self.switch_list[zone_id - 1]
            switch.set_state(switch_pressed=on_off)
        except Exception as err:
            print("[toggle_zone_switch] UGH ", err)

    def awning_toggle(self, state):
        # print(f'Toggle switch state {state}')
        on_off = state.get("onOff")
        if not on_off:
            return
        current_state = (
            self.HAL.movables.handler.state.get("awning", {})
            .get("light", {})
            .get("onOff")
        )
        if current_state == 1:
            self.HAL.movables.handler.move_awning({"onOff": 0})
        else:
            self.HAL.movables.handler.move_awning({"onOff": 1})

    def zone_switch(self, zone_id, in_on_off):
        if zone_id in CZONE_ZONES:
            result = czone.circuit_control(
                czone.cfg["mapping"].get(zone_id, zone_id), in_on_off, 100
            )
        elif zone_id in RVC_ZONES:
            # Get the stored brightness or default
            brightness = self.lighting_zone[zone_id].state.brt
            # Get the channel for this light
            can_instance = self.lighting_zone[zone_id].attributes.get('canInstance', 1)

            result = self.rvc.dc_dimmer_command(
                {
                    'onOff': in_on_off,
                    'brt': brightness
                },
                instance=can_instance
            )
        else:
            result = "Ok"
            controller_id = self._get_controller_id_from_zone(zone_id)
            print('Controller ID', controller_id)
            zone = "{:02X}".format(ZONE_TO_BIT.get(zone_id, 0xFF))
            if zone == "FF":
                # TODO: Switch CZone as well
                pass

            self.HAL.app.can_sender.can_send_raw('0CFC0044', f'{controller_id}06{zone}0100')

            try:
                zone_details = self.lighting_zone[zone_id]
            except KeyError as err:
                print(err)
                return

            zone_type = zone_details.type

            if zone_type == "dimmable":
                print('Handling dimmable light', zone_id)
                channel = self._is_channel_restricted(zone_id)
                if channel is not None:
                    rgbws = self.get_state(zone_id, "_rgb")
                    if rgbws is None:
                        rgbw = RGBW_DEFAULT.replace("#", "")
                    else:
                        rgbw = self.get_state(zone_id, "_rgb").replace("#", "")

                    print('Current Brightness', self.lighting_zone[zone_id].state.brt)
                    if self.lighting_zone[zone_id].state.brt == 0:
                        self.lighting_zone[zone_id].state.brt = BRIGHTNESS_DEFAULT

                    brightness = brightness_to_rgb_hex(self.lighting_zone[zone_id].state.brt)
                    rgbw_list = ["#"]
                    while rgbw:
                        rgbw_list.append(rgbw[:2])
                        rgbw = rgbw[2:]
                    if in_on_off == 1:
                        if channel == "R":
                            rgbw_list[1] = "{:02X}".format(brightness)
                        elif channel == "G":
                            rgbw_list[2] = "{:02X}".format(brightness)
                        elif channel == "B":
                            rgbw_list[3] = "{:02X}".format(brightness)
                        elif channel == "W":
                            rgbw_list[4] = "{:02X}".format(brightness)
                    else:
                        if channel == "R":
                            rgbw_list[1] = "00"
                        elif channel == "G":
                            rgbw_list[2] = "00"
                        elif channel == "B":
                            rgbw_list[3] = "00"
                        elif channel == "W":
                            rgbw_list[4] = "00"
                    rgb = "".join(rgbw_list)
                    rgb_result = self.zone_rgbw(zone_id, rgb)
                else:
                    print(f"Zone_id {zone_id} not reporting as using channel")

        # event_value = EventValues.ON if in_on_off == 1 else EventValues.OFF
        # self.event_logger.add_event(
        #     RVEvents.LIGHTING_ZONE_MODE_CHANGE, zone_id, event_value
        # )

        # TODO: This is all on if it worked as it appears - do we want all on here?
        if zone_id == 0:
            for z_id, zone in self.lighting_zone.items():
                self._update_state(z_id, {"onOff": in_on_off})
                zone.state.onOff = in_on_off
        else:
            self._update_state(zone_id, {"onOff": in_on_off})
            self.lighting_zone[zone_id].state.onOff = in_on_off

        return result

    def zone_brightness(self, zone_id: int, brightness: int):
        '''Set zone brightness.'''
        onOff = self.get_state(zone_id, "onOff")
        if zone_id in CZONE_ZONES:
            czone.circuit_control(
                czone.cfg["mapping"].get(zone_id, zone_id), onOff, brightness
            )
            # raise NotImplementedError('CZONE Brightness handling not yet implemented')

        elif zone_id in RVC_ZONES:
            # Get the stored onOff
            onOff = self.get_state(zone_id, "onOff")
            # Get the channel for this light
            can_instance = self.lighting_zone[zone_id].attributes.get('canInstance', 1)

            result = self.rvc.dc_dimmer_command(
                {
                    'onOff': onOff,
                    'brt': brightness
                },
                instance=can_instance
            )
        else:
            if brightness is None:
                brightness = BRIGHTNESS_DEFAULT
            else:
                if brightness < LED_MIN_BRIGHTNESS:
                    brightness = LED_MIN_BRIGHTNESS
                elif brightness > 100:
                    brightness = 100

            set_brightness = brightness_to_rgb_hex(brightness)
            channel = self._is_channel_restricted(zone_id)
            light_is_on = self.get_state(zone_id, "onOff")
            if channel is not None:
                rgbws = self.get_state(zone_id, "_rgb")
                if rgbws is None:
                    rgbw = RGBW_DEFAULT.replace("#", "")
                else:
                    rgbw = self.get_state(zone_id, "_rgb").replace("#", "")
                rgbw_list = ["#"]
                while rgbw:
                    rgbw_list.append(rgbw[:2])
                    rgbw = rgbw[2:]

                if light_is_on:
                    if channel == "R":
                        rgbw_list[1] = "{:02X}".format(set_brightness)
                    elif channel == "G":
                        rgbw_list[2] = "{:02X}".format(set_brightness)
                    elif channel == "B":
                        rgbw_list[3] = "{:02X}".format(set_brightness)
                    elif channel == "W":
                        rgbw_list[4] = "{:02X}".format(set_brightness)
                else:
                    if channel == "R":
                        rgbw_list[1] = "{:02X}".format(0)
                    elif channel == "G":
                        rgbw_list[2] = "{:02X}".format(0)
                    elif channel == "B":
                        rgbw_list[3] = "{:02X}".format(0)
                    elif channel == "W":
                        rgbw_list[4] = "{:02X}".format(0)

                rgb = "".join(rgbw_list)
                _ = self.zone_rgbw(zone_id, rgb)

            else:
                controller_id = self._get_controller_id_from_zone(zone_id)
                zone = "{:02X}".format(ZONE_TO_BIT.get(zone_id, 0xFF))
                brightness_hex = "{brightness:02X}{brightness:02X}".format(
                    brightness=brightness
                )
                self.HAL.app.can_sender.can_send_raw(
                    '0CFC0044',
                    f'{controller_id}03{zone}{brightness_hex}'
                )

        self._update_state(zone_id, {"brt": brightness})
        self.lighting_zone[zone_id].state.brt = brightness

        self.event_logger.add_event(
            RVEvents.LIGHTING_ZONE_BRIGHTNESS_LEVEL_CHANGE, zone_id, brightness
        )

        return self.lighting_zone[zone_id].state.brt

    def zone_rgbw(self, zone_id: int, rgbw: str):
        controller_id = self._get_controller_id_from_zone(zone_id)
        zone = "{:02X}".format(ZONE_TO_BIT.get(zone_id, 0xFF))
        rgb_value = rgbw.replace("#", "")

        # Disabled colorTemp
        # cmd = f"0CFC0044#{controller_id}3C{zone}00"
        self.HAL.app.can_sender.can_send_raw('0CFC0044', f'{controller_id}3C{zone}00')

        # Set controller to RBG mode
        # cmd = f"0CFC0044#{controller_id}02{zone}00"
        self.HAL.app.can_sender.can_send_raw('0CFC0044', f'{controller_id}02{zone}00')

        # cmd = f"0CFC0044#{controller_id}01{zone}{rgb_value}"
        self.HAL.app.can_sender.can_send_raw('0CFC0044', f'{controller_id}01{zone}{rgb_value}')
        # save the total RGB bytes in each circuit for the actual zone in the controller
        if zone_id in [1, 2, 3, 4]:
            for z in [1, 2, 3, 4]:
                self._update_state(z, {"_rgb": rgbw})
        elif zone_id in [5, 6, 7, 8]:
            for z in [5, 6, 7, 8]:
                self._update_state(z, {"_rgb": rgbw})
        elif zone_id in [9, 10, 11, 12]:
            for z in [9, 10, 11, 12]:
                self._update_state(z, {"_rgb": rgbw})
        elif zone_id in [13, 14, 15, 16]:
            for z in [13, 14, 15, 16]:
                self._update_state(z, {"_rgb": rgbw})

        return

    def notification(self, level):
        """Visualize notifications to the user based on criticality."""
        # Get current settings/state and store
        # Flash color of desired zones in this coach/product
        # Set back
        controller_id = self._get_controller_id_from_zone(0)
        zone = "{:02X}".format(ZONE_TO_BIT.get(0, 0xFF))

        if level == "error":
            color = "ff0000"
        elif level == "warning":
            color = "ffff00"
        else:
            color = "00ff00"

        for i in range(6):
            self.zone_rgb(0, color)
            time.sleep(0.5)
            self.zone_rgb(0, "ffffff")
            time.sleep(0.3)

    def update_can_state(self, msg_name: str, can_msg) -> dict:
        """
        Received CAN message lighting_broadcast
        {
            'Instance': 'Zone4',
            'Data2': 'Single Color',
            'Data3': '255',
            'Data4': '255',
            'Data5': '255',
            'Data6': '0',
            'Data7': '80',
            'Data8': '100',
            'msg': 'Timestamp: 1671520635.783745    ID: 0cfe20dc    X Rx                DL:  8    04 00 ff ff ff 00 50 64     Channel: canb0s0',
            'msg_name': 'Lighting_Broadcast',
            'instance_key':
            'CFE20DC__Zone4__NA'
        }
        Dec 20 07:17:17 WinnConnect .sh[1371]: Received CAN message lighting_broadcast {'Data1': 'Zone2', 'Data2': 'Single Color', 'Data3': '255', 'Data4': '255', 'Data5': '255', 'Data6': '0', 'Data7': '80', 'Data8': '100', 'msg': 'Timestamp: 1671520635.788805    ID: 0cfe20dc    X Rx                DL:  8    02 00 ff ff ff 00 50 64     Channel: canb0s0', 'msg_name': 'Lighting_Broadcast', 'instance_key': 'CFE20DC__Zone2__NA'}
        Dec 20 07:17:17 WinnConnect .sh[1371]: Received CAN message lighting_broadcast {'Data1': 'Zone1', 'Data2': 'Single Color', 'Data3': '255', 'Data4': '255', 'Data5': '255', 'Data6': '0', 'Data7': '80', 'Data8': '100', 'msg': 'Timestamp: 1671520635.794988    ID: 0cfe20dc    X Rx                DL:  8    01 00 ff ff ff 00 50 64     Channel: canb0s0', 'msg_name': 'Lighting_Broadcast', 'instance_key': 'CFE20DC__Zone1__NA'}
        Dec 20 07:17:17 WinnConnect  Received CAN message lighting_broadcast {'Data1': 'Zone3', 'Data2': 'Single Color', 'Data3': '36', 'Data4': '36', 'Data5': '36', 'Data6': '219', 'Data7': '100', 'Data8': '100', 'msg': 'Timestamp: 1671520635.798727    ID: 0cfe20dc    X Rx                DL:  8    03 00 24 24 24 db 64 64     Channel: canb0s0', 'msg_name': 'Lighting_Broadcast', 'instance_key': 'CFE20DC__Zone3__NA'}
        Dec 20 07:17:17 WinnConnect .sh[1371]: Received CAN message lighting_broadcast {'Data1': 'Zone4', 'Data2': 'Single Color', 'Data3': '255', 'Data4': '255', 'Data5': '255', 'Data6': '0', 'Data7': '64', 'Data8': '100', 'msg': 'Timestamp: 1671520635.803945    ID: 0cfe20dc    X Rx                DL:  8    04 00 ff ff ff 00 40 64     Channel: canb0s0', 'msg_name': 'Lighting_Broadcast', 'instance_key': 'CFE20DC__Zone4__NA'}
        Dec 20 07:17:17 WinnConnect .sh[1371]: Received CAN message lighting_broadcast {'Data1': 'Zone3', 'Data2': 'Single Color', 'Data3': '255', 'Data4': '255', 'Data5': '255', 'Data6': '0', 'Data7': '64', 'Data8': '100', 'msg': 'Timestamp: 1671520635.808818    ID: 0cfe20dc    X Rx                DL:  8    03 00 ff ff ff 00 40 64     Channel: canb0s0', 'msg_name': 'Lighting_Broadcast', 'instance_key': 'CFE20DC__Zone3__NA'}
        Dec 20 07:17:17 WinnConnect .sh[1371]: Received CAN message lighting_broadcast {'Data1': 'Zone2', 'Data2': 'Single Color', 'Data3': '255', 'Data4': '255', 'Data5': '255', 'Data6': '0', 'Data7': '64', 'Data8': '100', 'msg': 'Timestamp: 1671520635.813632    ID: 0cfe20dc    X Rx                DL:  8    02 00 ff ff ff 00 40 64     Channel: canb0s0', 'msg_name': 'Lighting_Broadcast', 'instance_key': 'CFE20DC__Zone2__NA'}
        Dec 20 07:17:17 WinnConnect .sh[1371]: Received CAN message lighting_broadcast {'Data1': 'Zone1', 'Data2': 'Single Color', 'Data3': '255', 'Data4': '255', 'Data5': '255', 'Data6': '0', 'Data7': '64', 'Data8': '100', 'msg': 'Timestamp: 1671520635.818642    ID: 0cfe20dc    X Rx                DL:  8    01 00 ff ff ff 00 40 64     Channel: canb0s0', 'msg_name': 'Lighting_Broadcast', 'instance_key': 'CFE20DC__Zone1__NA'}
        """
        # TODO: Implement handling of ITC zone status
        # TODO: Fix and bring back if needed

        if msg_name == 'lighting_broadcast':
            print('[LIGHTING] Broadcast received', can_msg)

            if self.itc_accept_state is False:
                # We got the initial state for each zone and no longer desire an update
                print(f'[LIGHTING] Broadcast parsing disabled "itc_accept_state": {self.itc_accept_state}')
                return {}

            itc_zone_id = int(can_msg.get("Instance").replace("Zone", ""))
            zone_mode = can_msg.get("Data2")
            zone_brightness = int(can_msg.get("Data7"))
            r = int(can_msg.get("Data3"))
            g = int(can_msg.get("Data4"))
            b = int(can_msg.get("Data5"))
            w = int(can_msg.get("Data6"))
            values = [r, g, b, w]
            print('[LIGHTING] Zone status received', itc_zone_id, zone_mode, zone_brightness)
            if zone_mode != 'Single Color':
                # Might be in Disco mode
                self.perform_reset()

            all_received = True
            for id, zone in self.itc_zones_status.items():
                if zone.get('received', False) is False:
                    all_received = False
                    break

            if all_received is True:
                self.itc_accept_state = False
            else:
                print('[LIGHTING] Updating ITC Zone', itc_zone_id)
                # Update the state for these lighting zones
                zone_offset = (itc_zone_id - 1) * 4
                for i in range(4):
                    value = values[i]
                    index = i + 1
                    zone_instance = zone_offset + index
                    print('[LIGHTING] LZ instance', zone_instance, zone_offset, index)
                    # Update the state here
                    try:
                        lighting_zone = self.lighting_zone[zone_instance]
                    except KeyError as err:
                        print('[LIGHTING] Zone not found, skipping', zone_instance)
                        continue

                    brightness = int(100 / 255 * value)
                    print('[LIGHTING] LZ brt', brightness)

                    if brightness == 0:
                        lighting_zone.state.brt = BRIGHTNESS_DEFAULT

                    if value == 0:
                        lighting_zone.state.onOff = EventValues.OFF
                    else:
                        lighting_zone.state.onOff = EventValues.ON

                    self.zone_brightness(zone_instance, lighting_zone.state.brt)
                    self.zone_switch(zone_instance, lighting_zone.state.onOff)

                    print(f'[LIGHTING] Updating Zone: {zone_instance}: {lighting_zone.state}')



                self.itc_zones_status[itc_zone_id]['received'] = True

        return {}

    def all_on(self):
        """Special function for 6 panel requirement."""
        # Note this could be done in a more harware specific and effecient way
        for zone_id, zone in self.lighting_zone.items():
            zone.state.onOff = 1
            if hasattr(zone.state, 'brt'):
                zone.state.brt = BRIGHTNESS_DEFAULT     # %
            zone.set_state(zone.state.dict())

        return "On"

    def all_off(self):
        """Special function for 6 panel requirement."""
        # Note this could be done in a more harware specific and effecient way
        for zone_id, zone in self.lighting_zone.items():
            if zone.attributes.get('hidden') is True:
                continue

            zone.state.onOff = 0
            zone.set_state(zone.state.dict())
            # self.zone_switch(z["id"], 0)
        return "Off"

    def set_zone_state(self, zone_id, state):
        '''Take a desired state of a light and perform required HW actions to set it.'''
        # Get the light obj
        # TODO: Do we need to handle key error here ? Probably not
        light_zone = self.lighting_zone[zone_id]
        if hasattr(state, 'brt'):
            if state.brt != light_zone.state.brt:
                # Only set it when brightness is different
                self.zone_brightness(zone_id, state.brt)

        self.zone_switch(zone_id, state.onOff)

        return light_zone.state


module_init = (
    Lighting,
    'lighting_mapping',
    'components'
)


if __name__ == "__main__":
    for i in range(1, 11):
        print(handler._get_controller_id_from_zone(i))
