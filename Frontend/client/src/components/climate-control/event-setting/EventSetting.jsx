import React from "react";
import {
  ActiveCool,
  ActiveHeat,
  Away,
  Camp,
  Sleep,
  Wake,
} from "../../../assets/asset";
import StartTime from "../start-time/StartTime";
import styles from "./index.module.css";

const iconObj = {
  Wake: <Wake />,

  Away: <Away />,

  "At Camp": <Camp />,

  Sleep: <Sleep />,
};

const EventSetting = ({ id, title, param, changeParam, clearEvent }) => {
  const toggleHot = (value) => {
    if (param.setTempHeat + value < param.setTempCool)
      changeParam("setTempHeat", param.setTempHeat + value);
  };
  const toggleCold = (value) => {
    if (param.setTempCool + value > param.setTempHeat)
      changeParam("setTempCool", param.setTempCool + value);
  };

  return (
    <div className={styles.container}>
      <div>
        <span style={{ verticalAlign: "middle", marginRight: "5px" }}>
          {iconObj[title]}
        </span>
        <span className={styles.title}>{title}</span>
      </div>
      <div className={styles.timer}>
        <StartTime param={param} changeParam={changeParam} title={title} />
      </div>
      <div className={styles.tempBox}>
        <div className={styles.heading}>Temp Range</div>
        <div className={styles.thermoContent}>
          <div
            className={`${styles.minusContainer} ${styles.orangeText}`}
            onClick={() => {
              toggleHot(-1);
            }}
          >
            -
          </div>
          <div
            className={`${styles.heatContainer} ${styles.orangeBorder} `}
            // onClick={() => setActiveBtn("HEAT")}
          >
            <div
              style={{ gap: "6px", padding: "0 10px" }}
              className="flex justify-center align-center"
            >
              <ActiveHeat />
              <h1 className={styles.tempText}>
                {param.setTempHeat}
                <span className={styles.fSmallText}>°F</span>
              </h1>
            </div>
          </div>

          <div
            className={`${styles.plusContainer} ${styles.orangeText}`}
            onClick={() => {
              toggleHot(+1);
            }}
          >
            +
          </div>
        </div>
        <br />
        <div className={styles.thermoContent}>
          <div
            className={`${styles.minusContainer} ${styles.blueText}`}
            onClick={() => {
              toggleCold(-1);
            }}
          >
            -
          </div>

          <div className={`${styles.coolContainer} ${styles.blueBorder} `}>
            <div
              style={{ gap: "6px", padding: "0 10px" }}
              className="flex justify-center align-center"
            >
              <ActiveCool />
              <h1 className={styles.tempText}>
                {param.setTempCool}
                <span className={styles.fSmallText}>°F</span>
              </h1>
            </div>
          </div>
          <div
            className={`${styles.plusContainer} ${styles.blueText}`}
            onClick={() => {
              toggleCold(+1);
            }}
          >
            +
          </div>
        </div>
      </div>
      <button className={styles.clearBtn} onClick={() => clearEvent(id)}>
        Clear Event
      </button>
    </div>
  );
};

export default EventSetting;
