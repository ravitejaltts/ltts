import React from "react";
import { Close } from "../../../assets/asset";
import { ClearNotificationBell } from "../../../assets/assets";
import styles from "./clear-noti.module.css";

const ClearAllNotificationModal = ({ data, close, onClear }) => {
  return (
    <div className={styles.container}>
      <span className={styles.closeBtn} onClick={close}>
        <Close />
      </span>
      <div>
        <div className={styles.bellIcon}>
          <ClearNotificationBell />
        </div>
        <h2 className={styles.title}>Clear all Notifications</h2>
        <h3 className={styles.description}>
          Are you sure you want to clear all notifications?
        </h3>
      </div>

      <div className={styles.btnContainer}>
        <button className={styles.cancelBtn} onClick={close}>
          Cancel
        </button>
        <button className={styles.rstBtn} onClick={onClear}>
          Clear
        </button>
      </div>
    </div>
  );
};

export default ClearAllNotificationModal;
