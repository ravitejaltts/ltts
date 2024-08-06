import React, { useState } from "react";
import { Close } from "../../../assets/asset";
import styles from "./fan.module.css";

const FanModal = ({ handleClose, setFanStatus, fanStatus }) => {
  const [activeBtn, setActiveBtn] = useState(fanStatus);
  const handleSetActive = (value) => {
    setActiveBtn(value);
    handleClose();
    setFanStatus(value);
  };
  console.log("typEE", typeof handleClose);
  return (
    <div className={styles.fanContainer}>
      <div className={styles.header}>
        <Close onClick={handleClose} className={styles.closeIcon} />
        <p className={styles.heading}>Fan</p>
      </div>
      <div className={styles.content}>
        <div className={styles.btnContainer}>
          <div
            className={`${styles.leftBtn} ${
              activeBtn === "On" && styles.activeBtn
            }`}
            onClick={() => handleSetActive("On")}
          >
            On
          </div>
          <div
            className={`${styles.heatBtn} ${
              activeBtn === "Off" && styles.activeBtn
            }`}
            onClick={() => handleSetActive("Off")}
          >
            Off
          </div>
          <div
            className={`${styles.rightBtn} ${
              activeBtn === "AUTO" && styles.activeBtn
            }`}
            onClick={() => handleSetActive("AUTO")}
          >
            Auto
          </div>
        </div>
      </div>
    </div>
  );
};

export default FanModal;
