import axios from "axios";
import moment from "moment-timezone";
import React, { useState } from "react";
import { DownArrow, UpArrow } from "../../../assets/asset";
import styles from "./index.module.css";

export const SetDateDialog = ({ data, close }) => {
  const [date, setDate] = useState(moment(data?.value));

  const dayChange = (value) => {
    const newDate = moment(date).add(value, "days");
    // console.log(newDate.format("MM DD YY"));
    setDate(newDate);
  };

  const monthChange = (value) => {
    const newDate = moment(date).add(value, "month");
    // console.log(newDate.format("MM DD YY"));
    setDate(newDate);
  };

  const yearChange = (value) => {
    const newDate = moment(date).add(value, "year");
    setDate(newDate);
  };

  const changeMainDate = () => {
    // axios
    if (data?.data?.[0]?.actions?.TAP?.action?.href) {
      axios
        .put(data?.data?.[0]?.actions?.TAP?.action?.href, {
          value: date.format("MM-DD-YYYY"),
        })
        .then((res) => {
          close();
        });
    }
  };

  return (
    <div className={styles.container}>
      <div>
        <div className={styles.daterMainContainer}>
          {/* month date */}
          <div className={styles.dateContainer}>
            <div className={styles.arrowBtn} onClick={() => monthChange(1)}>
              <UpArrow />
            </div>
            <div className={styles.textBox}>
              {date?.month() + 1}
              <span className={styles.label}>Month</span>
            </div>
            <div className={styles.arrowBtn} onClick={() => monthChange(-1)}>
              <DownArrow />
            </div>
          </div>
          {/* day date */}
          <div className={styles.dateContainer}>
            <div className={styles.arrowBtn} onClick={() => dayChange(1)}>
              <UpArrow />
            </div>
            <div className={styles.textBox}>
              {date?.date()}
              <span className={styles.label}>Day</span>
            </div>
            <div className={styles.arrowBtn} onClick={() => dayChange(-1)}>
              <DownArrow />
            </div>
          </div>

          {/* suffix date */}
          <div className={styles.dateContainer}>
            <div className={styles.arrowBtn} onClick={() => yearChange(1)}>
              <UpArrow />
            </div>
            <div className={`${styles.textBox} ${styles.year}`}>
              {date?.year().toString().slice(2)}
              <span className={styles.label}>Year</span>
            </div>
            <div className={styles.arrowBtn} onClick={() => yearChange(-1)}>
              <DownArrow />
            </div>
          </div>
        </div>
      </div>

      <div className={styles.btnContainer}>
        <button className={styles.cancelBtn} onClick={close}>
          Cancel
        </button>
        <button className={styles.setBtn} onClick={changeMainDate}>
          Set Date
        </button>
      </div>
    </div>
  );
};
