import React from "react";
import styles from "./index.module.css";
import axios from "axios";
import { Restart } from "../../../assets/asset";

const RestartDeviceDialog = ({ data, close }) => {
  console.log(data);
  function handleClose() {
    close();
  }
  function handleRestart() {
    console.log(data?.data?.[1]?.actions?.TAP?.actions);
    if (data?.data?.[1]?.actions?.TAP?.actions) {
      axios.put(data?.data?.[1]?.actions?.TAP?.actions?.href).then((res) => {
        close();
      });
    }
  }
  return (
    <div className={styles.container}>
      <div>
        <Restart />
        <h2 className={styles.title}>{data?.title}</h2>
        <h3 className={styles.description}>{data?.subtext}</h3>
      </div>

      <div className={styles.btnContainer}>
        <button className={styles.cancelBtn} onClick={handleClose}>
          {data?.data?.[0]?.title || "Cancel"}
        </button>
        <button className={styles.rstBtn} onClick={handleRestart}>
          {" "}
          {data?.data?.[1]?.title || "Restart"}
        </button>
      </div>
    </div>
  );
};

export default RestartDeviceDialog;
