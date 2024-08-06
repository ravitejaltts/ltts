import React from "react";
import styles from "./index.module.css";
import axios from "axios";
import { WipeRed } from "../../../assets/asset";

const WipeResetDialog = ({ data, close, open }) => {
  function handleClick() {
    if (data?.actions?.TAP?.action?.href) {
      axios
        .put(data?.actions?.TAP?.action?.href, {
          item: data?.actions?.TAP?.action?.params?.item,
          onOff: 1,
        })
        .then((res) => {
          open();
        });
    }
  }
  return (
    <div className={styles.container}>
      <div>
        <WipeRed />
        <h2 className={styles.title}>Wipe and Reset WinnConnect?</h2>
        <h3 className={styles.description}>
          <span>All Data will be wiped.</span> You can restore to previously
          saved configuration data after the reset. This does not inclue Wifi
          and Bluetooth configurations. Do you want to continue?
        </h3>
      </div>

      <div className={styles.btnContainer}>
        <button className={styles.cancelBtn} onClick={close}>
          Cancel
        </button>
        <button className={styles.wipeRstBtn} onClick={handleClick}>
          {data?.title}
        </button>
      </div>
    </div>
  );
};

export default WipeResetDialog;
