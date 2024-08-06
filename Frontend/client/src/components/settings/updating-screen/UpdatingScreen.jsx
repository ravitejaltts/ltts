import React from "react";
import styles from "./updating.module.css";
import { UpdatingLoader } from "../../../assets/asset";
import LOGO_DATA from "../../../assets/icon/settings/UpdateWinnebago.webp";

const UpdatingScreen = () => {
  return (
    <div className={styles.container}>
      <div className={styles.contentContainer}>
        <div>
          <img src={LOGO_DATA} className={styles.logoImage} />
        </div>
        <div className={styles.container2}>
          <p className={styles.text}>Updating...</p>
          <UpdatingLoader className={styles.loader} />
        </div>
      </div>
    </div>
  );
};

export default UpdatingScreen;
