import axios from "axios";
import React from "react";
import { Close, ITCBulb } from "../../../assets/asset";
import styles from "./index.module.css";

const LegalDisclamer = ({ data, close }) => {
  console.log(data);
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
        <h2 className={styles.title}>{data?.title}</h2>
        <h3 className={styles.subtitle}>{data?.subtext}</h3>
        <h4 className={styles.description}>{data?.body}</h4>
      </div>
    </div>
  );
};

export default LegalDisclamer;
