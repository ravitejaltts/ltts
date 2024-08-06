import React, { useEffect } from "react";
import styles from "./index.module.css";
import { WinnebagoLogo } from "../../../assets/asset";

const ResettingDialog = ({ close }) => {
  useEffect(() => {
    setTimeout(() => close(), 2000);
  }, []);
  return (
    <div className={styles.container}>
      <div className={styles.icon}>
        <WinnebagoLogo />
      </div>
      <h3 className={styles.title}>Resetting WinnConnect…</h3>
    </div>
  );
};

export default ResettingDialog;
