import React from "react";
import styles from "./index.module.css";
import logo from "../../../../assets/images/Winnebago_Pairing.webp";

const StartPairing = () => {
  return (
    <div className={styles.container}>
      <img src={logo} height="120px" width="120px" alt="pairing logo" />
      <h4 className={styles.title}>CONNECT YOUR PHONE</h4>
      <h2 className={styles.subtitle}>
        Connect Your RV to your phone throught the Winnebago App
      </h2>
      <p className={styles.description}>
        From your mobile device download the
        <span> Winnebago App </span>
        through ,<span> Google Play or Apple App stores </span>
        create your account and start pairing!
      </p>
      <button className={styles.startPairingBtn}>Start Pairing</button>
    </div>
  );
};

export default StartPairing;
