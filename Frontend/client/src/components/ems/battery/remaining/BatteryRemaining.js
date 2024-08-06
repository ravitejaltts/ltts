import React from "react";
import { EmsBattery } from "../../../../assets/asset";
import styles from "./remaining.module.css";

const BatteryRemaining = () => {
  return (
    <div className={styles.remaining}>
      <div className={styles.top}>
        <EmsBattery />
        <div>
          <h1>61%</h1>
          <p>Charge</p>
        </div>
      </div>
      <div className={styles.bottom}>
        <h2>Remaining</h2>
        <p>2 days 4 hrs</p>
      </div>
    </div>
  );
};

export default BatteryRemaining;
