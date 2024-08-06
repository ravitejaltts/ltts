import axios from "axios";
import React, { useState } from "react";
import { BackIcon, TempDown, TempUp } from "../../../assets/asset";
import Switch2 from "../../common/switch2/Switch2";
import { MAIN_MODE } from "../RefrigeratorSettings/constants";
import styles from "./index.module.css";

const TemperatureAlerts = ({
  data,
  setCurrentMode,
  refeshParentData = () => {},
}) => {
  const changeControlBoxState = () => {
    axios
      .put(data?.items[0]?.action_default?.action?.href, {
        onOff: data?.items[0].Simple?.onOff ? 0 : 1,
      })
      .then(() => {
        refeshParentData();
      });
  };
  const increaseTemp = (upperLimit, lowerLimit, key) => {
    axios
      .put(upperLimit?.change_upper_limit?.action?.href, {
        fdg_upper_limit: upperLimit?.value,
        fdg_lower_limit: lowerLimit?.value,
        ...(key === "fdg_upper_limit" && {
          fdg_upper_limit: upperLimit?.value + 1,
        }),
        ...(key === "fdg_lower_limit" && {
          fdg_lower_limit: lowerLimit?.value + 1,
        }),
      })
      .then(() => {
        refeshParentData();
      });
  };
  const decreaseTemp = (upperLimit, lowerLimit, key) => {
    axios
      .put(lowerLimit?.change_lower_limit?.action?.href, {
        fdg_upper_limit: upperLimit?.value,
        fdg_lower_limit: lowerLimit?.value,
        ...(key === "fdg_upper_limit" && {
          fdg_upper_limit: upperLimit?.value - 1,
        }),
        ...(key === "fdg_lower_limit" && {
          fdg_lower_limit: lowerLimit?.value - 1,
        }),
      })
      .then(() => {
        refeshParentData();
      });
  };

  const restoreDefaults = () => {
    axios.put(data?.items[2]?.action_default?.action?.href);
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

        <div className={styles.controlBox}>
          <div className={styles.thermoContent}>
            <div
              className={`${styles.minusContainer} ${styles.orangeText} `}
              style={{ fontSize: "70px" }}
              onClick={() =>
                // decreseTemp(data?.items?.[1]?.items?.[0], "fdg_upper_limit")
                decreaseTemp(
                  data?.items?.[1]?.items?.[0],
                  data?.items?.[1]?.items?.[1],
                  "fdg_upper_limit"
                )
              }
            >
              -
            </div>
            <div className={`${styles.heatContainer} ${styles.orangeBorder} `}>
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
                // increaseTemp(data?.items?.[1]?.items?.[0], "fdg_upper_limit")
                increaseTemp(
                  data?.items?.[1]?.items?.[0],
                  data?.items?.[1]?.items?.[1],
                  "fdg_upper_limit"
                )
              }
            >
              +
            </div>
          </div>
          <div className={styles.thermoContent}>
            <div
              className={`${styles.minusContainer} ${styles.blueText} `}
              style={{ fontSize: "70px" }}
              onClick={() =>
                // decreseTemp(data?.items?.[1]?.items?.[1], "fdg_lower_limit")
                decreaseTemp(
                  data?.items?.[1]?.items?.[0],
                  data?.items?.[1]?.items?.[1],
                  "fdg_lower_limit"
                )
              }
            >
              -
            </div>
            <div className={`${styles.heatContainer} ${styles.blueBorder} `}>
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
                // increaseTemp(data?.items?.[1]?.items?.[0], "fdg_upper_limit")
                increaseTemp(
                  data?.items?.[1]?.items?.[0],
                  data?.items?.[1]?.items?.[1],
                  "fdg_lower_limit"
                )
              }
            >
              +
            </div>
          </div>
        </div>

        <div className={styles.bottomBox}>
          <p className={styles.warning}>
            Warns when Fridge is outside of Temp Range.
          </p>

          <button className={styles.restoreBtn} onClick={restoreDefaults}>
            Restore Default
          </button>
        </div>
      </div>
    </div>
  );
};

export default TemperatureAlerts;
