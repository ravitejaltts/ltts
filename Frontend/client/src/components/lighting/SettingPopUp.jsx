import React, { useState } from "react";
import { SettingArrow, InfoIcon } from "../../assets/asset";
import styles from "./popup.module.css";

const SettingPopUp = () => {
  const [show, setShow] = useState(true);
  if (show)
    return (
      <div className={styles.popup}>
        <InfoIcon />
        <div className={styles.txt}>
          There is a burnt out light bulb in the Dinette group
          <br />
          <span onClick={() => setShow(false)}>Dismiss</span>
        </div>
        <SettingArrow />
      </div>
    );
  else {
    return null;
  }
};

export default SettingPopUp;
