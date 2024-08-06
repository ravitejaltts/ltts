import React, { useState } from "react";
import { MinusIcon, PlusIcon } from "../../../assets/asset";
import styles from "./temp.module.css";
import axios from "axios";
function TempController({ data, refreshDataImmediate }) {
  const handleReset = () => {
    if (data?.data?.[1]?.actions?.TAP?.action?.href) {
      axios.put(data?.data?.[1]?.actions?.TAP?.action?.href).then((res) => {
        refreshDataImmediate();
      });
    }
  };
  const handleChange = (val) => {
    if (data?.data?.[0]?.actions?.TAP?.action?.href) {
      axios
        .put(data?.data?.[0]?.actions?.TAP?.action?.href, {
          setTemp: val,
          unit: "F",
        })
        .then((res) => {
          refreshDataImmediate();
        });
    }
  };
  return (
    <>
      <div className={styles.controlBox}>
        <button
          className={styles.btns}
          onClick={() => handleChange(Number(data?.value) - 1)}
        >
          <MinusIcon />
        </button>
        <div className={styles.valueBox}>
          <span className={styles.tempValue}>{data?.value}</span>
          <span className={styles.tempSuffix}>&deg; F</span>
        </div>
        <button
          className={styles.btns}
          onClick={() => handleChange(Number(data?.value) + 1)}
        >
          <PlusIcon />
        </button>
      </div>
      <p className={styles.info}>{data?.data?.[0]?.subtext}</p>
      <div className={styles.restBtnContainer}>
        <button className={styles.resetBtn} onClick={handleReset}>
          {data?.data?.[1]?.title}
        </button>
      </div>
    </>
  );
}

export default TempController;
