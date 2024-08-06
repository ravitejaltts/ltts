import React, { useEffect, useState } from "react";
import { Backup, BackupFail } from "../../../../assets/asset";
import styles from "./index.module.css";

const BackingUpDialog = ({ close }) => {
  const [error, setError] = useState(false);
  const [value, setValue] = useState(0);
  useEffect(() => {
    if (value < 33) {
      setTimeout(() => incrementValue(), 100);
    } else {
      setError(true);
    }
  }, [value]);

  const incrementValue = () => {
    setValue((prev) => prev + 1);
  };
  console.log("Value", value);
  return (
    <div className={styles.container}>
      {error ? (
        <>
          <div className={styles.icon}>
            <BackupFail />
          </div>
          <h3 className={styles.titleError}>Backup Failed</h3>
          <h4 className={styles.description}>
            Couldn’t complete your configuratioin data backup, please check your
            connection and try again{" "}
          </h4>
          <button className={styles.okayBtn} onClick={close}>
            Okay
          </button>
        </>
      ) : (
        <>
          <Backup />

          <progress
            className={styles.progress}
            id="file"
            value={value}
            max="100"
          >
            {" "}
            32%{" "}
          </progress>
          <h3 className={styles.title}>Backing Up Configuration Data…</h3>
        </>
      )}
    </div>
  );
};

export default BackingUpDialog;
