import React from "react";
import { AlertCritical, AlertWarning } from "../../assets/assets";
import styles from "./noti-center.module.css";

const AlertIconBox = ({ type, active }) => {
  if (type === 0)
    return (
      <div
        className={styles.alertIconBox}
        style={{ background: `${active ? "red" : "#d1d1d6"}` }}
      >
        <AlertCritical />
      </div>
    );
  if (type === 1)
    return (
      <div
        className={styles.alertIconBox}
        style={{ background: `${active ? "#f7a300" : "#d1d1d6"}` }}
      >
        <AlertWarning />
      </div>
    );
  else {
    return (
      <div
        className={styles.alertIconBox}
        style={{ background: `${active ? "red" : "#f7a300"}` }}
      >
        <AlertWarning />
      </div>
    );
  }
};

export default AlertIconBox;
