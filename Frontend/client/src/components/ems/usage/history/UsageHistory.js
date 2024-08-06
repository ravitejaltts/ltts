import React from "react";
import { useNavigate } from "react-router-dom";
import styles from "./history.module.css";

const Meter = ({ level, ungrouped }) => {
  return (
    <div
      className={`${styles.meterDivContainer} ${
        ungrouped && styles.ungroupedMeter
      } ${level === "0%" && styles.emptyMeter}`}
    >
      <div className={`${styles.meterFill} `} style={{ height: level }}></div>
    </div>
  );
};

const UsageHistory = () => {
  const navigate = useNavigate();
  return (
    <div className={styles.history}>
      <p>Today</p>
      <div className={styles.metersContainer}>
        <Meter level="70%" />
        <Meter level="70%" />
        <Meter level="70%" />
        <Meter level="70%" />
        <Meter level="70%" />
      </div>
      <div onClick={() => navigate("history")} className={styles.historyButton}>
        See history
      </div>
    </div>
  );
};

export default UsageHistory;
