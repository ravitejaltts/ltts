import React from "react";
import styles from "./summary.module.css";

const UsageSummary = () => {
  return (
    <div className={styles.summary}>
      <div class={styles.ringContainer}>
        <div class={styles.ring}></div>
        <div
          class={styles.ringOverlay}
          style={{
            transform: `rotate(50deg)`,
          }}
        ></div>
      </div>
    </div>
  );
};

export default UsageSummary;
