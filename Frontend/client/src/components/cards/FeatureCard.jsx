import React from "react";
import styles from "./feature.module.css";

function FeatureCard({ icon, color, heading, subHeading, onClick, topRightText, topRightTitle }) {
  return (
    <div className={styles.container} onClick={onClick}>
      <div className={styles.topRow}>
        <div className={`${color} ${styles.iconContainer}`}>{icon}</div>
        <div className={styles.topRightContent}>
          <span>{topRightTitle}</span>
          <span>{topRightText}</span>
        </div>
      </div>
      <div>
        <p className={styles.centerHeading}>{heading}</p>
        <p className={styles.bottomText}>{subHeading}</p>
      </div>
    </div>
  );
}

export default FeatureCard;
