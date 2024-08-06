import React from "react";
import styles from "./pairing.module.css";
import { PairingRV, RVPairing } from "../../../assets/assets";

const PairingSuccess = ({ close }) => {
  return (
    <div className={styles.successContainer}>
      <img src={RVPairing} />
      <p className={styles.progressMsg1}>Success!</p>
      <p className={styles.progressMsg2}>You’re now connected.</p>
      <button className={styles.btn3} onClick={close}>
        Okay
      </button>
    </div>
  );
};

export default PairingSuccess;
