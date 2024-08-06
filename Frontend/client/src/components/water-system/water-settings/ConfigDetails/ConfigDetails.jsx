import axios from "axios";
import React from "react";
import { BackIcon, MinusIcon, PlusIcon } from "../../../../assets/asset";
import SettingRow from "../../../lighting/SettingRow";
import styles from "./config.module.css";

const ConfigDetails = ({
  config,
  setConfigDetailIndex,
  refreshDataImmediate,
}) => {
  console.log("config!!", config);

  const changeUnit = (value) => {
    axios
      .put(config?.items[0].action_default?.action?.href, {
        value: value,
        item: "VolumeUnitPreference",
      })
      .then((res) => {
        refreshDataImmediate();
      })
      .catch((err) => console.error(err));
  };

  const handleRestoreDefault = (configItem) => {
    axios
      .put(`${configItem?.actions?.PRESS?.action?.href}`)
      .then(() => refreshDataImmediate());
  };

  const handleIncreaseTemp = (configItem, mode) => {
    console.log("configItem", configItem);
    let step = 1;
    if (configItem?.state?.unit == "C") {
      step = 0.5;
    }
    axios
      .put(configItem?.actions?.TAP?.action?.href, {
        setTemp:
          mode === "inc"
            ? configItem?.state?.setTemp + step
            : configItem?.state?.setTemp - step,
        unit: configItem?.state?.unit,
      })
      .then(() => refreshDataImmediate());
  };

  return (
    <>
      {config?.type === "WATER_TEMPERATURE" ? (
        <>
          <div className={styles.header}>
            <div
              className={styles.back}
              onClick={() => setConfigDetailIndex(-1)}
            >
              <BackIcon />
              <h2 className={styles.backText}>Back</h2>
            </div>
            <p className={styles.heading}>
              {config?.items?.length && config?.items[0]?.title}
            </p>
          </div>

          {config?.items?.map((configItem) => {
            if (configItem?.widget === "TEMPERATURE_SETTING") {
              return (
                <div className={styles.thermoContent}>
                  <div
                    className={`${styles.minusContainer} ${styles.orangeText}`}
                    onClick={() => handleIncreaseTemp(configItem, "dec")}
                  >
                    <MinusIcon />
                  </div>

                  <div
                    className={`${styles.heatContainer} ${styles.orangeBorder}`}
                    onClick={() => {}}
                  >
                    <div
                      style={{ gap: "6px", padding: "0 10px" }}
                      className="flex justify-center align-center"
                    >
                      <h1 className={styles.tempText}>
                        {configItem?.state?.unit === "C"
                          ? configItem?.state?.setTemp?.toFixed(1)
                          : configItem?.state?.setTemp}
                        <span className={styles.fSmallText}>
                          °{configItem?.state?.unit}
                        </span>
                      </h1>
                    </div>
                  </div>

                  <div
                    className={`${styles.plusContainer} ${styles.orangeText}`}
                    onClick={() => handleIncreaseTemp(configItem, "inc")}
                  >
                    <PlusIcon />
                  </div>
                </div>
              );
            }
            if (configItem?.widget === "SIMPLE_BUTTON") {
              return (
                <div className={styles.bottomBox}>
                  <button
                    className={styles.restoreBtn}
                    onClick={() => handleRestoreDefault(configItem)}
                  >
                    Restore Default
                  </button>
                </div>
              );
            }
          })}
        </>
      ) : (
        <div>
          <div className={styles.header}>
            <div
              className={styles.back}
              onClick={() => setConfigDetailIndex(-1)}
            >
              <BackIcon />
              <h2>Back</h2>
            </div>
            <p className={styles.heading}>Unit Preferences</p>
          </div>
          <div className={styles.infoContainer} style={{ marginTop: "20px" }}>
            {config?.items[0]?.options?.map((option, ind, arr) => (
              <div key={ind} onClick={() => changeUnit(option.value)}>
                <SettingRow
                  name={option.key}
                  selected={option.selected}
                  value={option.value}
                  noBorder={ind === arr.length - 1}
                />
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
};

export default ConfigDetails;
