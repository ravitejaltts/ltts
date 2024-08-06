import React, { useState } from "react";
import { MinusIcon, PlusIcon, TempDown, TempUp } from "../../../assets/asset";
import Switch2 from "../../common/switch2/Switch2";
import styles from "./fridge.module.css";
import axios from "axios";

const FridgeController = ({ data, refreshDataImmediate }) => {
  const [contolBox, setControlBox] = useState(data?.[0]?.state?.onoff);
  const changeControlBoxState = () => {
    if (data?.[0]?.actions?.TOGGLE?.action) {
      axios
        .put(data?.[0]?.actions?.TOGGLE?.action?.href, {
          onOff: Number(!data?.[0]?.state?.onoff),
        })
        .then((res) => {
          refreshDataImmediate();
        });
    }
    // setControlBox((prev) => !prev);
  };

  const increaseTemp = (upperLimit, lowerLimit, key) => {
    axios
      .put(upperLimit?.actions?.TAP?.action?.href, {
        fdg_upper_limit: upperLimit?.value,
        fdg_lower_limit: lowerLimit?.value,
        ...(key === "fdg_upper_limit" && {
          fdg_upper_limit: upperLimit?.value + 1,
        }),
        ...(key === "fdg_lower_limit" && {
          fdg_lower_limit: lowerLimit?.value + 1,
        }),
      })
      .then((res) => {
        refreshDataImmediate();
      });
  };
  const decreaseTemp = (upperLimit, lowerLimit, key) => {
    axios
      .put(lowerLimit?.actions?.TAP?.action?.href, {
        fdg_upper_limit: upperLimit?.value,
        fdg_lower_limit: lowerLimit?.value,
        ...(key === "fdg_upper_limit" && {
          fdg_upper_limit: upperLimit?.value - 1,
        }),
        ...(key === "fdg_lower_limit" && {
          fdg_lower_limit: lowerLimit?.value - 1,
        }),
      })
      .then((res) => {
        refreshDataImmediate();
      });
  };
  function handleReset() {
    if (data?.[1]?.items?.[2]?.actions?.TAP?.action?.href) {
      axios
        .put(data?.[1]?.items?.[2]?.actions?.TAP?.action?.href)
        .then((res) => {
          refreshDataImmediate();
        });
    }
  }
  return (
    <div>
      <div>
        <div
          className={`${styles.infoContainer} ${!contolBox && styles.closed}`}
        >
          <div className={styles.row}>
            <span>{data?.[0]?.title}</span>
            <div className={styles.switchContainer}>
              <span className={styles.switchValue}>
                {data?.[0]?.state?.onoff ? "On" : "Off"}
              </span>
              <Switch2
                onOff={data?.[0]?.state?.onoff}
                action={changeControlBoxState}
              />
            </div>
          </div>
        </div>
        {!!data?.[0]?.state?.onoff && (
          <div className={styles.controlBox}>
            <div className={styles.thermoContent}>
              <div
                className={`${styles.minusContainer} ${styles.orangeText} `}
                style={{ fontSize: "70px" }}
                onClick={() =>
                  decreaseTemp(
                    data?.[1]?.items?.[0],
                    data?.[1]?.items?.[1],
                    "fdg_upper_limit"
                  )
                }
              >
                <MinusIcon />
              </div>

              <div>
                <p className={styles.boxHeading}>
                  {data?.[1]?.items?.[0]?.title}
                </p>
                <div
                  className={`${styles.heatContainer} ${styles.orangeBorder} `}
                >
                  <div
                    style={{ gap: "6px" }}
                    className="flex justify-center align-center"
                  >
                    <TempUp />{" "}
                    <h1 className={styles.tempText}>
                      {data?.[1]?.items?.[0]?.value}
                    </h1>
                    <span className={styles.fSmallText}>°F</span>
                  </div>
                </div>
              </div>

              <div
                className={`${styles.plusContainer} ${styles.orangeText} `}
                onClick={() =>
                  increaseTemp(
                    data?.[1]?.items?.[0],
                    data?.[1]?.items?.[1],
                    "fdg_upper_limit"
                  )
                }
              >
                <PlusIcon />
              </div>
            </div>
            <div className={styles.thermoContent}>
              <div
                className={`${styles.minusContainer} ${styles.blueText} `}
                style={{ fontSize: "70px" }}
                onClick={() =>
                  decreaseTemp(
                    data?.[1]?.items?.[0],
                    data?.[1]?.items?.[1],
                    "fdg_lower_limit"
                  )
                }
              >
                <MinusIcon />
              </div>
              <div>
                <p className={styles.boxHeading}>
                  {data?.[1]?.items?.[1]?.title}
                </p>
                <div
                  className={`${styles.heatContainer} ${styles.blueBorder} `}
                >
                  <div
                    style={{ gap: "6px" }}
                    className="flex justify-center align-center"
                  >
                    <TempDown />{" "}
                    <h1 className={styles.tempText}>
                      {data?.[1]?.items?.[1]?.value}
                    </h1>
                    <span className={styles.fSmallText}>°F</span>
                  </div>
                </div>
              </div>

              <div
                className={`${styles.plusContainer} ${styles.blueText} `}
                onClick={() =>
                  increaseTemp(
                    data?.[1]?.items?.[0],
                    data?.[1]?.items?.[1],
                    "fdg_lower_limit"
                  )
                }
              >
                <PlusIcon />
              </div>
            </div>
          </div>
        )}
      </div>
      <div className={styles.bottomBox}>
        <p className={styles.warning}>{data?.[1]?.items?.[2]?.subtext}</p>
        {!!data?.[0]?.state?.onoff && (
          <div className={styles.restBtnContainer}>
            <button className={styles.resetBtn} onClick={handleReset}>
              {data?.[1]?.items?.[2]?.title}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default FridgeController;
