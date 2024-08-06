import React, { useState } from "react";
import { DownArrow, SettingArrow, UpArrow } from "../../../assets/asset";
import styles from "./index.module.css";

const StartTime = ({ title, param, changeParam }) => {
  const [timeDialog, setTimeDialog] = useState(false);

  const toggleTimeDialog = () => {
    setTimeDialog((prev) => !prev);
  };

  const hourChange = (value) => {
    let newValue = param.startHour + value;
    if (newValue === 13) {
      newValue = 1;
    } else if (newValue === 0) {
      newValue = 12;
    }
    changeParam("startHour", newValue);
  };

  const minChange = (value) => {
    let newValue = Number(param?.startMinute) + value;
    if (newValue === 60) {
      newValue = 0;
    } else if (newValue === 0) {
      newValue = 59;
    }
    if (String(newValue).length === 1) {
      newValue = "0" + newValue;
    }
    changeParam("startMinute", newValue);
  };
  const suffixChange = () => {
    if (param.startTimeMode === "AM") {
      return changeParam("startTimeMode", "PM");
    }
    return changeParam("startTimeMode", "AM");
  };
  return (
    <div className={styles.container}>
      <div className={styles.first}>
        <div>Start Time</div>
        {!timeDialog && (
          <div className={styles.rightDiv} onClick={toggleTimeDialog}>
            <div>
              {param?.startHour}:{param.startMinute}
              {param.startTimeMode}
            </div>
            <SettingArrow />
          </div>
        )}
      </div>
      {timeDialog && (
        <div>
          <div className={styles.timerMainContainer}>
            {/* hour time */}
            <div className={styles.timeContainer}>
              <div className={styles.arrowBtn} onClick={() => hourChange(+1)}>
                <UpArrow />
              </div>
              <div className={styles.textBox}>{param?.startHour}</div>
              <div className={styles.arrowBtn} onClick={() => hourChange(-1)}>
                <DownArrow />
              </div>
            </div>
            {/* minute time */}
            <div className={styles.timeContainer}>
              <div className={styles.arrowBtn} onClick={() => minChange(+1)}>
                <UpArrow />
              </div>
              <div className={styles.textBox}>{param?.startMinute}</div>
              <div className={styles.arrowBtn} onClick={() => minChange(-1)}>
                <DownArrow />
              </div>
            </div>
            {/* suffix time */}
            <div className={styles.timeContainer}>
              <div className={styles.arrowBtn} onClick={suffixChange}>
                <UpArrow />
              </div>
              <div className={styles.textBox}>{param?.startTimeMode}</div>
              <div className={styles.arrowBtn} onClick={suffixChange}>
                <DownArrow />
              </div>
            </div>
          </div>
          <button className={styles.setTimeBtn} onClick={toggleTimeDialog}>
            Set Time
          </button>
        </div>
      )}
    </div>
  );
};

export default StartTime;
