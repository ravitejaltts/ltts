import React from "react";
import styles from "./pairing.module.css";
import { PairingRV, RVPairing } from "../../../assets/assets";

const PairingProgress = () => {
  return (
    <div className={styles.progressContainer}>
      <div className={styles.imageContainer}>
        <img className={styles.rvImage} src={RVPairing} />
        <div className={styles.bubble} />
        <div className={styles.bubble2} />
      </div>
      <p className={styles.progressMsg1}>Connecting your Device</p>
      <p className={styles.progressMsg2}>This should only take a minute</p>
    </div>
  );
};

export default PairingProgress;
