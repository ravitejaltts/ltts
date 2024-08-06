import React from "react";
import styles from "./updating.module.css";
import { Close } from "../../../assets/asset";

const AboutUpdate = ({ data, close }) => {
  return (
    <div className={styles.container}>
      <div>
        <Close onClick={close} className={styles.closeIcon} />
      </div>
      <div className={styles.contentContainer}>
        <div>
          <p className={styles.textHeader}>{data?.title}</p>
        </div>
        <div className={styles.container2}>
          <div
            className={styles.textSub}
            dangerouslySetInnerHTML={{ __html: data?.text_page }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export default AboutUpdate;
