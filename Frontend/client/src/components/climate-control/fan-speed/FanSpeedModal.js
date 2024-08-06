import React, { useState } from "react";
import { Close } from "../../../assets/asset";
import styles from "./speed.module.css";

const FanSpeedModal = ({ handleClose, fanSpeed, setFanSpeed }) => {
  const [activeBtn, setActiveBtn] = useState(fanSpeed);
  const handleSetActive = (value) => {
    setActiveBtn(value);
    handleClose();
    setFanSpeed(value);
  };
  console.log("typEE", handleClose);
  return (
    <div className={styles.fanContainer}>
      <div className={styles.header}>
        <Close onClick={handleClose} className={styles.closeIcon} />
        <p className={styles.heading}>Speed</p>
      </div>
      <div className={styles.content}>
        <div className={styles.btnContainer}>
          <div
            className={`${styles.leftBtn} ${
              activeBtn === "Low" && styles.activeBtn
            }`}
            onClick={() => handleSetActive("Low")}
          >
            Low
          </div>
          <div
            className={`${styles.heatBtn} ${
              activeBtn === "Mid" && styles.activeBtn
            }`}
            onClick={() => handleSetActive("Mid")}
          >
            Mid
          </div>
          <div
            className={`${styles.rightBtn} ${
              activeBtn === "High" && styles.activeBtn
            }`}
            onClick={() => handleSetActive("High")}
          >
            High
          </div>
        </div>
      </div>
    </div>
  );
};

export default FanSpeedModal;
