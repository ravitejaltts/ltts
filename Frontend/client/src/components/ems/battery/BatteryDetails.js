import React from "react";
import styles from "./details.module.css";

const DetailCard = () => {
  return (
    <div className={styles.detailCard}>
      <p className={styles.detailTopText}>Power</p>
      <h3 className={styles.detailMiddleText}>87</h3>
      <p className={styles.detailBottomText}>Watts</p>
    </div>
  );
};

const BatteryDetails = () => {
  return (
    <div className={styles.details}>
      <div className={styles.topRow}>
        <h3>Battery details</h3>
        <div className={styles.tabs}>
          <div className={styles.tab}>All</div>
          <div className={styles.tab}>Pack 1</div>
          <div className={styles.tab}>Pack 2</div>
        </div>
      </div>
      <div className={styles.cardsContainer}>
        <DetailCard />
        <DetailCard />
        <DetailCard />
        <DetailCard />
        <DetailCard />
      </div>
    </div>
  );
};

export default BatteryDetails;
