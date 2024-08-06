import React from "react";
import styles from "./sensitivity.module.css";
import Slider from "rc-slider";
import axios from "axios";

const SensitivityController = ({ data, refresh }) => {
  console.log(data?.state?.mtnSense);
  const handleAction = (value) => {
    if (data?.actions?.SLIDE?.action?.href) {
      axios
        .put(data?.actions?.SLIDE?.action?.href, {
          mtnSense: value,
        })
        .then(() => {
          refresh();
        });
    }
  };
  return (
    <div>
      <div className={styles.header}>
        <p>LEAST SENSITIVE</p>
        <p>MOST SENSITIVE</p>
      </div>
      <div className={styles.slider}>
        <Slider
          trackStyle={{ backgroundColor: "#4c85a9" }}
          railStyle={{ backgroundColor: "#e5e5ea" }}
          max={data?.widget?.max || 5}
          min={data?.widget?.min || 5}
          step={data?.widget?.step || 5}
          // defaultValue={3}
          value={data?.state?.mtnSense}
          onChange={handleAction}
          dots
        />
        <div className={styles.numContainer}>
          {[1, 2, 3, 4, 5].map((num) => (
            <span key={num}>{num}</span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SensitivityController;
