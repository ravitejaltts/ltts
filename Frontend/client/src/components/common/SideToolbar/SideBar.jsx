import React, { useContext, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  NavBarApps,
  NavBarDisplay,
  NavBarHome,
  NavBarNotification,
  NavBarSettings,
} from "../../../assets/assets";
import {
  NOTIFICATION_TYPES,
  PAGE_LINKS,
  SCREEN_COLOR_NOTIFICATION,
} from "../../../constants/CONST";
import styles from "./index.module.css";
import { MainContext } from "../../../context/MainContext";

function SideToolBar() {
  const location = useLocation();
  const { notificationData } = useContext(MainContext);

  const navigate = useNavigate();

  return (
    <div className={styles.sidebarContainer}>
      <div>
        <div onTouchStart={() => navigate(PAGE_LINKS.HOME)}>
          <div
            className={styles.iconContainer}
            active={location?.pathname === PAGE_LINKS.HOME ? "true" : "false"}
          >
            <NavBarHome />
          </div>
        </div>
        <div onTouchStart={() => navigate(PAGE_LINKS.APPS)}>
          <div
            className={styles.iconContainer}
            active={location?.pathname === PAGE_LINKS.APPS ? "true" : "false"}
          >
            <NavBarApps />
          </div>
        </div>
      </div>

      <div>
        <div className={styles.appDivider} />
        <div onTouchStart={() => navigate(PAGE_LINKS.NOTIFICATION)}>
          <div
            className={`${styles.iconContainer} ${styles.notificationIconBox}`}
            active={
              location?.pathname === PAGE_LINKS.NOTIFICATION ? "true" : "false"
            }
          >
            <NavBarNotification />
            <span
              className={`${styles.notiCount} ${
                notificationData.type === NOTIFICATION_TYPES.CRITICAL &&
                styles.critcal
              } ${
                notificationData.type === NOTIFICATION_TYPES.INFO && styles.info
              } ${
                notificationData.type === NOTIFICATION_TYPES.WARNING &&
                styles.warning
              }`}
            >
              {notificationData?.length > 0 && notificationData?.length}
            </span>
          </div>
        </div>
        <div onTouchStart={() => navigate(PAGE_LINKS.SETTINGS)}>
          <div
            className={styles.iconContainer}
            active={
              location?.pathname === PAGE_LINKS.SETTINGS ? "true" : "false"
            }
          >
            <NavBarSettings />
          </div>
        </div>
        <div onTouchStart={() => navigate(PAGE_LINKS.SETTING_DISPLAY)}>
          <div
            className={styles.iconContainer}
            active={
              location?.pathname === PAGE_LINKS.SETTING_DISPLAY
                ? "true"
                : "false"
            }
          >
            <NavBarDisplay />
          </div>
        </div>
      </div>
    </div>
  );
}

export default SideToolBar;
