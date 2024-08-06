import React, { useState } from "react";
import { AlertCritical, AlertWarning } from "../../assets/assets";
import styles from "./noti-center.module.css";

const getPriority = (priority) => {
  if (priority <= 1) {
    return "critical";
  } else if (priority <= 3) {
    return "warning";
  } else if (priority >= 4) {
    return "information";
  }
};

const AlertIcon = ({ priority }) => {
  const [type, setType] = useState(getPriority(priority));

  if (type === "critical")
    return (
      <div className={styles.alertIcon} style={{ background: "red" }}>
        <AlertCritical />
      </div>
    );
  if (type === "warning")
    return (
      <div className={styles.alertIcon} style={{ background: "#f7a300" }}>
        <AlertWarning />
      </div>
    );
  //  need icon for information
  if (type === "information")
    return (
      <div className={styles.alertIcon} style={{ background: "#f7a300" }}>
        <AlertWarning />
      </div>
    );

    return (
      <div className={styles.alertIcon} style={{ background: "#f7a300" }}>
        <AlertWarning />
      </div>
    );
};

export default AlertIcon;
