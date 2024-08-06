import React from "react";
import styles from "./pairing.module.css";
import { PairingErrorIcon } from "../../../assets/assets";

const PairingError = ({ close }) => {
  const tryAgainPairing = () => {};
  return (
    <div className={styles.errorContainer}>
      <PairingErrorIcon />
      <p className={styles.progressMsg1}>Couldn’t Connect your Device</p>
      <p className={styles.progressMsg2}>
        Some help text with possible solutions the user could take, such as
        making sure the phone is awake and on the right screen and close enough
        to the HMI
      </p>
      <div className={styles.btnContainer}>
        <button className={styles.btn1} onClick={close}>
          Cancel
        </button>
        <button className={styles.btn2} onClick={tryAgainPairing}>
          Try Again
        </button>
      </div>
    </div>
  );
};

export default PairingError;
