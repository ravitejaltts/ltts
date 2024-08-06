import React from "react";
import { BlueThermostat, RoundAlert } from "../../../../assets/asset";
import styles from "./index.module.css";

const HistoryItem = ({ data, ind, length }) => {
  return (
    <div
      className={`${styles.itemContainer} ${ind === 0 && styles.firstItem} ${
        ind === length - 1 && styles.lastItem
      }`}
    >
      {data?.alert ? <RoundAlert /> : <BlueThermostat />}
      <div className={styles.itemTextContainer}>
        <h2 className={styles.itemMainText}>
          Fridge temp at {data?.text || "33°"}
        </h2>
        <p className={styles.itemDate}>{data?.time}</p>
      </div>
    </div>
  );
};

export default HistoryItem;
