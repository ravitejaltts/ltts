import React from "react";
import { useNavigate } from "react-router-dom";
import { BackIcon } from "../../../assets/asset";
import UsageHistory from "../../../components/ems/usage/history/UsageHistory";
import UsageSummary from "../../../components/ems/usage/summary/UsageSummary";
import UsageDetails from "../../../components/ems/usage/UsageDetails";
import styles from "./usage.module.css";

const Usage = () => {
  const navigate = useNavigate();
  return (
    <div className={styles.usage}>
      <div className={styles.backNav} onClick={() => navigate(-1)}>
        <BackIcon />
        <p className={styles.backText}>Back</p>
        <p className={styles.energyText}>Battery Details</p>
      </div>
      <div className={styles.mainContainer}>
        {/* left div */}
        <div className={styles.leftContainer}>
          <UsageDetails />
        </div>
        {/* right container for 2 divs */}
        <div className={styles.rightContainer}>
          <UsageSummary />
          <UsageHistory />
        </div>
      </div>
    </div>
  );
};

export default Usage;
