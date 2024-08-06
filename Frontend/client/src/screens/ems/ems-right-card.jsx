import React from "react";
import styles from "./ems.module.css";

function EmsRightCard(topText, bottomText, name, ind, iconObj) {
  return (
    <div key={ind} className={styles.rightCard}>
      <div className={styles.iconBox}>{iconObj[name]}</div>
      <div className={styles.rightTexts}>
        <p className={styles.cardTopText}>{topText}</p>
        <p className={styles.bottomText} style={{ fontSize: "15px" }}>
          {bottomText}
        </p>
      </div>
    </div>
  );
}

export default EmsRightCard;
