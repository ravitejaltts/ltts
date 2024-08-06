import JSON_DATA from "../constants/rv_values.json";
export const SETTINGS_LINKS = {
  LAYOUT: "/setting/",
  REVEL: "UiSettingAboutTab",
  CONNECTIVITY: "UiSettingsConnectivity",
  FEATURES: "UiSettingsFeatures",
  NOTIFICATIONS: "UiSettingsNotifications",
  UNIT_PREFERENCES: "UiSettingsUnitPreferences",
  SYSTEM: "UiSettingsSystem",
  SOFTWARE_UPDATE: "UiSettingsSoftwareUpdate",
  DISPLAY: "UiSettingsDisplay",
  FEATURES_CLIMATE_CONTROL: "UiSettingsFeaturesDetailsClimate",
  FEATURES_ENERGY: "UiSettingsFeaturesDetailsEnergy",
  FEATURES_INVERTER: "UiSettingsFeaturesDetailsInverter",
  FEATURES_LIGHTS: "UiSettingsFeaturesDetailsLights",
  FEATURES_PET: "UiSettingsFeaturesDetailsPetMonitor",
  FEATURES_REFRIDGERATOR: "UiSettingsFeaturesDetailsRefrigerator",
  FEATURES_WATER: "UiSettingsFeaturesDetailsWaterSystems",
};

export const PAGE_LINKS = {
  HOME: "/",
  SETTINGS: "/setting/UiSettingAboutTab",
  SETTING_DISPLAY: "/setting/UiSettingsDisplay",
  APPS: "/my-rv",
  NOTIFICATION: "/notification-center",
};
export const NOTIFICATION_TYPES = {
  CRITICAL: "CRITICAL",
  WARNING: "WARNING",
  INFO: "INFO",
  NONE: "NONE",
};

export const UPDATE_SCREEN_VALUES = {
  UPDATING: "UPDATING",
  UPDATING_FAILED: "UPDATING_FAILED",
  ABOUT_UPDATE: "ABOUT_UPDATE",
};

export const SCREEN_COLOR_NOTIFICATION = {
  [NOTIFICATION_TYPES.CRITICAL]: "linear-gradient(135deg, #9a0000, black)",
  [NOTIFICATION_TYPES.WARNING]: "linear-gradient(135deg, #945701, black)",
  [NOTIFICATION_TYPES.INFO]: "linear-gradient(135deg, #0e5369, black)",
};

export const PET_SEVERITY_TYPE = {
  DEFAULT: "DEFAULT",
  WARNING: "WARNING",
  CRITICAL: "CRITICAL",
  INFO: "INFO",
};

export const PET_SEVERITY_BG_COLOR = {
  [PET_SEVERITY_TYPE.DEFAULT]:
    "linear-gradient(320deg, #55b966 -89%, #000000 81%)",
  [PET_SEVERITY_TYPE.WARNING]:
    "linear-gradient(320deg, #f7a300 -89%, #000000 81%)",
  [PET_SEVERITY_TYPE.CRITICAL]:
    "linear-gradient(320deg, #f15f31 -89%, #000000 81%)",
  [PET_SEVERITY_TYPE.INFO]:
    "linear-gradient(320deg, #419bf9 -89%, #000000 81%)",
};

export const PET_VAR_DEFAULT_COLOR = {
  [PET_SEVERITY_TYPE.DEFAULT]: "#55b966",
  [PET_SEVERITY_TYPE.WARNING]: "#f7a300",
  [PET_SEVERITY_TYPE.CRITICAL]: "#f15f31",
  [PET_SEVERITY_TYPE.INFO]: "#419bf9",
};
export const getEventValues = () => {
  const EVENT_MAP = {};
  if (JSON_DATA) {
    for (let obj of JSON_DATA) {
      EVENT_MAP[obj.name] = obj.value;
    }
  }
  return EVENT_MAP;
};

export const BACKGROUND_PRIORITY = {
  NOTIFICATION: "NOTIFICATION",
  PET_MONITORING: "PET_MONITORING",
};

export const EVENTVALUES = getEventValues();
