import React, { useContext } from "react";
import { MainContext } from "../../../context/MainContext";
import { NOTIFICATION_TYPES } from "../../../constants/CONST";
import styles from "./index.module.css";
import NotiCritical from "../../../assets/icons/notification/critical.png";
import NotiInfo from "../../../assets/icons/notification/info.png";
import NotiWarning from "../../../assets/icons/notification/warning.png";
import NotiDefault from "../../../assets/icons/notification/default.png";

const NotificationIcon = () => {
  const { notificationData } = useContext(MainContext);
  if (notificationData.type === NOTIFICATION_TYPES.CRITICAL) {
    return (
      <img
        src={NotiCritical}
        className={styles.critical}
        style={{
          // height: `${40 + (40 * percent.toFixed(0)) / 100}px`,
          // width: `${40 + (40 * percent.toFixed(0)) / 100}px`,

          height: "64px",
          width: "64px",
        }}
      />
    );
  }
  if (notificationData.type === NOTIFICATION_TYPES.INFO) {
    return (
      <img
        src={NotiInfo}
        className={styles.info}
        style={{
          // height: `${40 + (40 * percent.toFixed(0)) / 100}px`,
          // width: `${40 + (40 * percent.toFixed(0)) / 100}px`,
          height: "64px",
          width: "64px",
        }}
      />
    );
  }
  if (notificationData.type === NOTIFICATION_TYPES.WARNING) {
    return (
      <img
        src={NotiWarning}
        className={styles.warning}
        style={{
          // height: `${40 + (40 * percent.toFixed(0)) / 100}px`,
          // width: `${40 + (40 * percent.toFixed(0)) / 100}px`,
          height: "64px",
          width: "64px",
        }}
      />
    );
  } else {
    return (
      <img
        src={NotiDefault}
        style={{
          height: "64px",
          width: "64px",
        }}
      />
    );
  }
};

export default NotificationIcon;
