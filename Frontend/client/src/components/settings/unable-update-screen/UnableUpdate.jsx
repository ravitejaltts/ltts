import React from "react";
import styles from "./updating.module.css";
import { Close, UpdatingError } from "../../../assets/asset";

const UnableUpdate = ({ data, close, retryHandler }) => {
  return (
    <div className={styles.container}>
      <div className={styles.contentContainer}>
        <UpdatingError />
        <p className={styles.text1}>Unable to Update Software</p>
        <p className={styles.text2}>
          Your software couldn’t be updated at this time. If you continue to
          have issues, please contact customer support at
        </p>
        <p className={styles.text3}>1-833-714-1224</p>

        <div className={styles.container2}>
          <button className={styles.btn1} onClick={retryHandler}>
            Retry
          </button>
          <button className={styles.btn2} onClick={close}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default UnableUpdate;
