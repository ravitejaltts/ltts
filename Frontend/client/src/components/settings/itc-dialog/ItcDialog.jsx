import axios from "axios";
import React from "react";
import { Close, ITCBulb } from "../../../assets/asset";
import styles from "./index.module.css";

const ItcDialog = ({ data, close }) => {
  function handleRestart() {
    if (data?.[1]?.actions?.TAP?.action?.href) {
      axios.put(data?.[1]?.actions?.TAP?.action?.href).then((res) => {
        close();
      });
    }
  }
  return (
    <div className={styles.container}>
      <span className={styles.closeBtn} onClick={close}>
        <Close />
      </span>
      <div>
        <ITCBulb />
        <h2 className={styles.title}>{data?.[0]?.title}</h2>
        <h3 className={styles.description}>{data?.[0]?.subtext}</h3>
      </div>

      <div className={styles.btnContainer}>
        <button className={styles.rstBtn} onClick={handleRestart}>
          {data?.[1]?.title || "Restart"}
        </button>
      </div>
    </div>
  );
};

export default ItcDialog;
