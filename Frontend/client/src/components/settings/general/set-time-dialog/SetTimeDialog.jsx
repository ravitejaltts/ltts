import React, { useState } from "react";
import { DownArrow, UpArrow } from "../../../../assets/asset";
import styles from "./index.module.css";

export const SetTimeDialog = ({ close, changeTime, defaultTime }) => {
  const [time, setTime] = useState(defaultTime);

  const toggleTime = (key, value) => {
    setTime((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const hourChange = (value) => {
    let newValue = Number(time.hour) + value;
    if (newValue === 13) {
      newValue = 1;
    } else if (newValue === 0) {
      newValue = 12;
    }
    toggleTime("hour", newValue);
  };

  const minChange = (value) => {
    let newValue = Number(time?.minutes) + value;
    if (newValue === 60) {
      newValue = 0;
    } else if (newValue === 0) {
      newValue = 59;
    }
    if (String(newValue).length === 1) {
      newValue = "0" + newValue;
    }
    toggleTime("minutes", newValue);
  };

  const suffixChange = () => {
    if (time.mode === "AM") {
      return toggleTime("mode", "PM");
    }
    return toggleTime("mode", "AM");
  };

  const changeMainTime = () => {
    changeTime(time);
    close();
  };
  return (
    <div className={styles.container}>
      <div>
        <div className={styles.timerMainContainer}>
          {/* hour time */}
          <div className={styles.timeContainer}>
            <div className={styles.arrowBtn} onClick={() => hourChange(1)}>
              <UpArrow />
            </div>
            <div className={styles.textBox}>{time?.hour}</div>
            <div className={styles.arrowBtn} onClick={() => hourChange(-1)}>
              <DownArrow />
            </div>
          </div>
          {/* minute time */}
          <div className={styles.timeContainer}>
            <div className={styles.arrowBtn} onClick={() => minChange(1)}>
              <UpArrow />
            </div>
            <div className={styles.textBox}>{time?.minutes}</div>
            <div className={styles.arrowBtn} onClick={() => minChange(-1)}>
              <DownArrow />
            </div>
          </div>
          {/* suffix time */}
          <div className={styles.timeContainer}>
            <div className={styles.arrowBtn} onClick={suffixChange}>
              <UpArrow />
            </div>
            <div className={`${styles.textBox} ${styles.mode}`}>
              {time?.mode}
            </div>
            <div className={styles.arrowBtn} onClick={suffixChange}>
              <DownArrow />
            </div>
          </div>
        </div>
      </div>

      <div className={styles.btnContainer}>
        <button className={styles.cancelBtn} onClick={close}>
          Cancel
        </button>
        <button className={styles.setBtn} onClick={changeMainTime}>
          Set Clock
        </button>
      </div>
    </div>
  );
};
