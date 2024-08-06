import React from "react";
import { Link } from "react-router-dom";
import {
  SettingFeature,
  SettingLogo,
  SettingNotification,
  SettingSystem,
  SettingUnit,
  SettingWifi,
  SettingUpdate,
  SettingDisplay,
  SettingClose,
} from "../../../assets/asset";
import { SETTINGS_LINKS } from "../../../constants/CONST";
import styles from "./sidebar.module.css";

const iconObj = {
  UiSettingAboutTab: <SettingLogo />,
  UiSettingsConnectivity: <SettingWifi />,
  UiSettingsFeatures: <SettingFeature />,
  UiSettingsNotifications: <SettingNotification />,
  UiSettingsUnitPreferences: <SettingUnit />,
  UiSettingsSystem: <SettingSystem />,
  UiSettingsSoftwareUpdate: <SettingUpdate />,
  UiSettingsDisplay: <SettingDisplay />,
};

function SideBar({ active = SETTINGS_LINKS.REVEL, tabs }) {
  return (
    <div className={styles.sideBar}>
      {tabs?.map(({ title, name, EOS }) => (
        <React.Fragment key={title}>
          <div
            className={`${styles.link} ${styles.logo} ${
              active === `/setting/${name}` && styles.active
            }`}
          >
            <Link to={`/setting/${name}`}>
              {iconObj[name]} {title}
            </Link>
          </div>
          {EOS && <div className={styles.divider} />}
        </React.Fragment>
      ))}
      {/* <div
        className={`${styles.link} ${styles.logo} ${
          active === `/setting/${SETTINGS_LINKS.CONNECTIVITY}` && styles.active
        }`}
      >
        <Link to={`/setting/${SETTINGS_LINKS.CONNECTIVITY}`}>
          {iconObj[SETTINGS_LINKS.CONNECTIVITY]} {"CONNECTIVITY"}
        </Link>
      </div> */}
    </div>
  );
}

export default SideBar;
