import React from "react";
import { Away, Camp, Sleep, Wake } from "../../../assets/asset";
import styles from "./index.module.css";

const iconObj = {
  Wake: <Wake />,

  Away: <Away />,

  "At Camp": <Camp />,

  Sleep: <Sleep />,
};

const SchedulerRow = ({
  id,
  title,
  name,
  setTempCool,
  setTempHeat,
  startHour,
  startMinute,
  startTimeMode,
}) => {
  return (
    <>
      <div className={styles.row}>
        <div>
          <span style={{ verticalAlign: "middle", marginRight: "5px" }}>
            {iconObj[title]}
          </span>
          <span
            className={setTempCool ? styles.activeText : styles.disabledText}
          >
            {title}
          </span>
        </div>
        {setTempCool ? (
          <div className={styles.details}>
            <span className={styles.time}>
              {startHour}:
              {String(startMinute).length === 1
                ? "0" + startMinute
                : startMinute}{" "}
              {startTimeMode}
            </span>{" "}
            <span className={styles.hot}>{setTempHeat}</span>{" "}
            <span className={styles.period}>.</span>
            <span className={styles.cold}> {setTempCool}</span>
          </div>
        ) : (
          <div className={styles.disabled}>Tap to Set</div>
        )}
      </div>
    </>
  );
};

export default SchedulerRow;
