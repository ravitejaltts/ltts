import React from "react";
import { useNavigate } from "react-router-dom";
import { BackIcon } from "../../../assets/asset";
import BatteryDetails from "../../../components/ems/battery/BatteryDetails";
import BatteryHistory from "../../../components/ems/battery/history/BatteryHistory";
import BatteryRemaining from "../../../components/ems/battery/remaining/BatteryRemaining";
import styles from "./battery.module.css";

const Battery = () => {
  const navigate = useNavigate();
  return (
    <div className={styles.battery}>
      <div className={styles.backNav} onClick={() => navigate(-1)}>
        <BackIcon />
        <p className={styles.backText}>Back</p>
        <p className={styles.energyText}>Battery Details</p>
      </div>
      <div className={styles.mainContainer}>
        {/* left div */}
        <div className={styles.leftContainer}>
          <BatteryDetails />
        </div>
        {/* right container for 2 divs */}
        <div className={styles.rightContainer}>
          <BatteryRemaining />
          <BatteryHistory />
        </div>
      </div>
    </div>
  );
};

export default Battery;
