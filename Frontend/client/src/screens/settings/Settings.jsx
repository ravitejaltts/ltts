import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { BackIcon, SettingsIcon } from "../../assets/asset";
import {
  BluetoothIcon,
  NotificationsIcon,
  WifiIcon,
} from "../../assets/settingsIcons";
import AboutMyRv from "../../components/settings/general/about-my-rv/AboutMyRv";
import SoftwareUpdates from "../../components/settings/general/software-updates/SoftwareUpdates";

import General from "../../components/settings/general/General";

import { AppContext } from "../../context/AppContext";
import Bluetooth from "../../components/settings/bluetooth/Bluetooth";
import UserDetail from "../../components/settings/bluetooth/user-detail/UserDetail";
import DataBackup from "../../components/settings/general/data-backup/DataBackup";
import DisplaySettings from "../../components/settings/general/display-settings/DisplaySettings";
import FeatureSettings from "../../components/settings/general/feature-setting/FeatureSetting";
import InnerSettings from "../../components/settings/general/feature-setting/inner-settings/InnerSettings";
import TimeAndLocation from "../../components/settings/general/time-and-location/TimeAndLocation";
import UnitPreferences from "../../components/settings/general/unit-preference/UnitPreference";
import WipeAndReset from "../../components/settings/general/wipe-and-reset/WipeAndReset";
import { DataContext } from "../../context/DataContext";
import { useFetch } from "../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../utils/api";
import styles from "./settings.module.css";

const tabs = [
  {
    id: 1,
    icon: <SettingsIcon />,
    text: "General",
  },
  {
    id: 2,
    icon: <BluetoothIcon />,
    text: "Bluetooth",
  },
  {
    id: 3,
    icon: <NotificationsIcon />,
    text: "Notifications",
  },
  {
    id: 4,
    icon: <WifiIcon />,
    text: "Connectivity",
  },
];

const iconObj = {
  SettingsMenuGeneral: <SettingsIcon />,
  SettingsMenuBluetooth: <BluetoothIcon />,
  SettingsMenuNotifications: <NotificationsIcon />,
  SettingsMenuConnectivity: <WifiIcon />,
};

const Setting = () => {
  const navigate = useNavigate();
  const { pollingInterval } = useContext(AppContext);
  const { data, refreshDataImmediate } = useFetch(
    API_ENDPOINT.SETTING,
    LOCAL_ENDPOINT.SETTING,
    true,
    pollingInterval
  );
  const [activeSetting, setActiveSetting] = useState(0);
  const [activeData, setActiveData] = useState(null);
  const changeActiveSetting = (id) => setActiveSetting(id);

  const [showInnerFeatures, setInnerFeatures] = useState(false);

  const [url, setUrl] = useState(null);
  useEffect(() => {
    setUrl(window.location.pathname);
  }, [window.location.pathname]);

  return (
    <DataContext.Provider
      value={{
        refreshParentData: refreshDataImmediate,
      }}
    >
      <div className={styles.settingsContainer}>
        <div className={styles.left}>
          <div onClick={() => navigate("/")} className={styles.tab}>
            <BackIcon />
            <p>Settings</p>
          </div>
          {data?.data?.map((tab, i) => (
            <div
              onClick={() => {
                navigate("/settings");
                changeActiveSetting(i);
              }}
              key={i}
              className={`${styles.tab} ${
                activeSetting === i && styles.activeTab
              }`}
            >
              {iconObj[tab.name]}
              <p>{tab?.title}</p>
            </div>
          ))}
          {tabs.map(({ icon, text, id }) => (
            <div
              onClick={() => {
                navigate("/settings");
                changeActiveSetting(id);
              }}
              key={id}
              className={`${styles.tab} ${
                activeSetting === id && styles.activeTab
              }`}
            >
              {icon}
              <p>{text}</p>
            </div>
          ))}
        </div>
        <div className={styles.right}>
          {activeSetting === 0 && url === "/settings" && (
            <General data={data && data?.data[0]} />
          )}
          {activeSetting === 1 && url === "/settings" && (
            <Bluetooth data={data && data?.data[1]} />
          )}
          {activeSetting === 2 && url === "/settings" && "Notification"}
          {activeSetting === 3 && url === "/settings" && "Connectivity"}
          {url === "/settings/About%20My%20RV" && (
            <AboutMyRv data={data?.data[0]?.data?.configuration[0]?.data[0]} />
          )}
          {url === "/settings/Software%20Updates" && (
            <SoftwareUpdates
              data={data?.data[0]?.data?.configuration[0]?.data[1]}
            />
          )}
          {url === "/settings/Display" && (
            <DisplaySettings
              data={data && data?.data[0]?.data?.configuration[1]?.data?.[0]}
            />
          )}
          {url === "/settings/Time%20and%20Location" && (
            <TimeAndLocation
              data={data?.data[0]?.data?.configuration[1]?.data[1]}
            />
          )}
          {url === "/settings/Unit%20Preferences" && (
            <UnitPreferences
              data={data?.data[0]?.data?.configuration[1]?.data[2]}
            />
          )}

          {url === "/settings/Feature%20Settings" && showInnerFeatures ? (
            <InnerSettings setInnerFeatures={setInnerFeatures} />
          ) : url === "/settings/Feature%20Settings" ? (
            <FeatureSettings
              setInnerFeatures={setInnerFeatures}
              data={data?.data[0]?.data?.configuration[1]?.data[3]}
            />
          ) : (
            ""
          )}

          {url === "/settings/Data%20Backup" && (
            <DataBackup data={data?.data[0]?.data?.configuration[2]?.data[0]} />
          )}
          {url === "/settings/Wipe%20and%20Reset%20WinnConnect" && (
            <WipeAndReset
              data={data?.data[0]?.data?.configuration[2]?.data[1]}
            />
          )}
          {url === "/settings/user-detail" && <UserDetail />}
        </div>
      </div>
    </DataContext.Provider>
  );
};

export default Setting;
