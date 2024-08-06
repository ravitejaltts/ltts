import axios from "axios";
import React, { useState } from "react";
import { BackIcon, TempDown, TempUp } from "../../../assets/asset";
import Switch2 from "../../../components/common/switch2/Switch2";
import { MAIN_MODE } from "../RefrigeratorSettings/constants";
import styles from "./index.module.css";

const TemperatureAlerts = ({
  data,
  setCurrentMode,
  refeshParentData = () => {},
  currentMode,
}) => {
  console.log("alert data", data);
  const changeControlBoxState = () => {
    axios
      .put(data?.items[0]?.action_default?.action?.href, {
        onOff: data?.items[0].Simple?.onOff ? 0 : 1,
        applianceType:
          data?.items[0]?.action_default?.action?.params?.applianceType,
      })
      .then(() => {
        refeshParentData();
      });
  };
  const increaseTemp = (upperLimit, lowerLimit, key) => {
    axios
      .put(upperLimit?.change_upper_limit?.action?.href, {
        upper_limit: upperLimit?.value,
        lower_limit: lowerLimit?.value,
        ...(key === "upper_limit" && {
          upper_limit: upperLimit?.value + 1,
        }),
        ...(key === "lower_limit" && {
          lower_limit: lowerLimit?.value + 1,
        }),
        applianceType:
          upperLimit?.change_upper_limit?.action?.params?.applianceType,
      })
      .then(() => {
        refeshParentData();
      });
  };
  const decreaseTemp = (upperLimit, lowerLimit, key) => {
    axios
      .put(lowerLimit?.change_lower_limit?.action?.href, {
        upper_limit: upperLimit?.value,
        lower_limit: lowerLimit?.value,
        ...(key === "upper_limit" && {
          upper_limit: upperLimit?.value - 1,
        }),
        ...(key === "lower_limit" && {
          lower_limit: lowerLimit?.value - 1,
        }),
        applianceType:
          lowerLimit?.change_lower_limit?.action?.params?.applianceType,
      })
      .then(() => {
        refeshParentData();
      });
  };

  const restoreDefaults = () => {
    axios.put(data?.items[2]?.action_default?.action?.href, {
      applianceType:
        data?.items[2]?.action_default?.action?.params?.applianceType,
    });
  };
  return (
    <div>
      <div className={styles.header}>
        <div className={styles.back} onClick={() => setCurrentMode(MAIN_MODE)}>
          <BackIcon />
          <h2>Back</h2>
        </div>
        <p className={styles.heading}>Temp Alert</p>
      </div>
      <div>
        <div className={styles.infoContainer}>
          <div className={styles.row}>
            <span>{data?.items[0]?.title}</span>
            <div>
              <Switch2
                onOff={data?.items[0].Simple?.onOff}
                action={changeControlBoxState}
              />
            </div>
          </div>
        </div>
        {!data?.items[0]?.Simple?.onOff && (
          <p className={`${styles.ifTxt}`}>
            Receive an alert when the freezer temp goes beyond the high and low
            temperature thresholds.
          </p>
        )}
        {data?.items && data?.items[0]?.Simple?.onOff && (
          <>
            <div className={styles.controlBox}>
              <div className={styles.thermoContent}>
                <div
                  className={`${styles.minusContainer} ${styles.orangeText} `}
                  style={{ fontSize: "70px" }}
                  onClick={() =>
                    // decreseTemp(data?.items?.[1]?.items?.[0], "upper_limit")
                    decreaseTemp(
                      data?.items?.[1]?.items?.[0],
                      data?.items?.[1]?.items?.[1],
                      "upper_limit"
                    )
                  }
                >
                  -
                </div>
                <div
                  className={`${styles.heatContainer} ${styles.orangeBorder} `}
                >
                  <div
                    style={{ gap: "6px" }}
                    className="flex justify-center align-center"
                  >
                    <TempUp />{" "}
                    <h1 className={styles.tempText}>
                      {data?.items?.[1]?.items?.[0]?.value}
                    </h1>
                    <span className={styles.fSmallText}>°F</span>
                  </div>
                </div>

                <div
                  className={`${styles.plusContainer} ${styles.orangeText} `}
                  onClick={() =>
                    // increaseTemp(data?.items?.[1]?.items?.[0], "upper_limit")
                    increaseTemp(
                      data?.items?.[1]?.items?.[0],
                      data?.items?.[1]?.items?.[1],
                      "upper_limit"
                    )
                  }
                >
                  +
                </div>
              </div>
              <p className={`${styles.ifTxt}`}>
                If the {currentMode === "fridge-control" ? "fridge" : "freezer"}{" "}
                temp goes above this number, you will get an alert.
              </p>
              <div className={styles.thermoContent}>
                <div
                  className={`${styles.minusContainer} ${styles.blueText} `}
                  style={{ fontSize: "70px" }}
                  onClick={() =>
                    // decreseTemp(data?.items?.[1]?.items?.[1], "lower_limit")
                    decreaseTemp(
                      data?.items?.[1]?.items?.[0],
                      data?.items?.[1]?.items?.[1],
                      "lower_limit"
                    )
                  }
                >
                  -
                </div>
                <div
                  className={`${styles.heatContainer} ${styles.blueBorder} `}
                >
                  <div
                    style={{ gap: "6px" }}
                    className="flex justify-center align-center"
                  >
                    <TempDown />{" "}
                    <h1 className={styles.tempText}>
                      {data?.items?.[1]?.items?.[1]?.value}
                    </h1>
                    <span className={styles.fSmallText}>°F</span>
                  </div>
                </div>

                <div
                  className={`${styles.plusContainer} ${styles.blueText} `}
                  onClick={() =>
                    // increaseTemp(data?.items?.[1]?.items?.[0], "upper_limit")
                    increaseTemp(
                      data?.items?.[1]?.items?.[0],
                      data?.items?.[1]?.items?.[1],
                      "lower_limit"
                    )
                  }
                >
                  +
                </div>
              </div>
              <p className={`${styles.ifTxt}`}>
                If the {currentMode === "fridge-control" ? "fridge" : "freezer"}{" "}
                temp goes below this number, you will get an alert.
              </p>
            </div>

            <div className={styles.bottomBox}>
              <button className={styles.restoreBtn} onClick={restoreDefaults}>
                Restore Default
              </button>
            </div>
            <p className={styles.warning}>
              The optimal{" "}
              {currentMode === "fridge-control" ? "fridge" : "freezer"}{" "}
              temperature range is 0°F or below.
            </p>
          </>
        )}
      </div>
    </div>
  );
};

export default TemperatureAlerts;
