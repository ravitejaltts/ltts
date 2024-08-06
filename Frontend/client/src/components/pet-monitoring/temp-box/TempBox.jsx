import axios from "axios";
import React from "react";
import { BackIcon, TempDown, TempUp } from "../../../assets/asset";
import Switch2 from "../../common/switch2/Switch2";
import styles from "./temp.module.css";

const TempBox = ({ data, refeshParentData = () => {}, enable }) => {
  const changeTemp = (val, action , unit) => {
    if (action?.CHANGE?.action?.href) {
      axios
        .put(action?.CHANGE?.action?.href, {
          unit,
          ...(action?.CHANGE?.action?.params?.$maxTemp && { maxTemp: val }),
          ...(action?.CHANGE?.action?.params?.$minTemp && { minTemp: val }),
        })
        .finally(() => {
          refeshParentData();
        });
    }
  };
  return (
    <div className={`${styles.container} ${!enable && styles.disabled}`}>
      {!enable && <div className={styles.overlay} />}
      <div className={styles.header}>
        <p className={`${styles.ifTxt}`}>{data?.text}</p>
      </div>
      <div>
        <div className={styles.controlBox}>
          <p className={`${styles.boxTitle} ${!enable && styles.disabledText}`}>
            {data?.title}
          </p>
          {data?.items?.map((tempData , i) => (
            <div key={i}>
              <p
                className={`${styles.tempTitle} ${
                  !enable && styles.disabledText
                }`}
              >
                {tempData?.title}
              </p>
              <div className={styles.thermoContent}>
                <div
                  className={`${styles.minusContainer} ${
                    !enable && styles.disabledText
                  } ${
                    tempData?.type === "TEMP_SETTING_HOT"
                      ? styles.orangeText
                      : styles.blueText
                  } `}
                  style={{ fontSize: "70px" }}
                  onClick={() =>
                    changeTemp(Number(tempData?.value) - tempData?.step, tempData?.actions , tempData?.state?.unit)
                  }
                >
                  -
                </div>
                <div
                  className={`${styles.heatContainer} ${
                    !enable && styles.disabledBorder
                  } ${
                    tempData?.type === "TEMP_SETTING_HOT"
                      ? styles.orangeBorder
                      : styles.blueBorder
                  } `}
                >
                  <div className={styles.valueBox}>
                    <h1
                      className={`${styles.tempText} ${
                        !enable && styles.disabledText
                      }`}
                    >
                      {tempData?.value}
                    </h1>
                    <span
                      className={`${styles.fSmallText} ${
                        !enable && styles.disabledText
                      }`}
                    >
                      °{tempData?.state?.unit}
                    </span>
                  </div>
                </div>
                <div
                  className={`${styles.plusContainer} ${
                    !enable && styles.disabledText
                  } ${
                    tempData?.type === "TEMP_SETTING_HOT"
                      ? styles.orangeText
                      : styles.blueText
                  } `}
                  onClick={() =>
                    changeTemp(Number(tempData?.value) + tempData?.step, tempData?.actions, tempData?.state?.unit)
                  }
                >
                  +
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TempBox;
