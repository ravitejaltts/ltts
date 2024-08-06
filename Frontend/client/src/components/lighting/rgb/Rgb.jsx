import Wheel from "@uiw/react-color-wheel";
import React, { useState } from "react";
import { useEffect } from "react";
import styles from "./rgb.module.css";
import Temp from "./Temp";

const Rgb = ({ data, setData, callAction, setRefetch, color, setColor }) => {
  const [mode, setMode] = useState("Color");
  const changeColor = (value) => {
    setRefetch(false);
    setColor(value)
    setData((prev) => {
      return { ...prev, rgb: value };
    });
  };
  const changeMode = (value) => {
    setMode(value);
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      if(color) {
        callAction({rgb: color})
      }
    } , 50)
    return () => clearTimeout(timer)
  } , [color])

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.title}>{mode}</div>
        <div className={styles.typeSelector}>
          <button
            className={`${styles.type1} ${mode === "Color" && styles.active}`}
            onClick={() => changeMode("Color")}
          >
            Color
          </button>
          <button
            className={`${styles.type2} ${mode === "White" && styles.active}`}
            onClick={() => changeMode("White")}
          >
            White
          </button>
        </div>
      </div>
      {mode === "Color" ? (
        <>
          <div className={styles.rgbBox}>
            <Wheel
              height={280}
              width={280}
              prefixCls={styles.colorWheel}
              color={color ? color : data.rgb}
              onChange={(color) => changeColor(color.hex)}
              onTouchEnd={() => changeColor(data.rgb)}
            />
          </div>
          <div className={styles.sampleBox}>
            <div
              className={styles.sample}
              style={{ background: "#fff3eb" }}
              onTouchStart={() => changeColor("#fff3eb")}
              onTouchEnd={() => callAction({ rgb: data.rgb })}
            ></div>
            <div
              className={styles.sample}
              style={{ background: "#ffd587" }}
              onTouchStart={() => changeColor("#ffd587")}
              onTouchEnd={() => callAction({ rgb: data.rgb })}
            ></div>
            <div
              className={styles.sample}
              style={{ background: "#ff0000" }}
              onTouchStart={() => changeColor("#ff0000")}
              onTouchEnd={() => callAction({ rgb: data.rgb })}
            ></div>
            <div
              className={styles.sample}
              style={{ background: "#00ff00" }}
              onTouchStart={() => changeColor("#00ff00")}
              onTouchEnd={() => callAction({ rgb: data.rgb })}
            ></div>
            <div
              className={styles.sample}
              style={{ background: "#0000ff" }}
              onTouchStart={() => changeColor("#0000ff")}
              onTouchEnd={() => callAction({ rgb: data.rgb })}
            ></div>
          </div>
        </>
      ) : (
        <Temp
          data={data}
          setData={setData}
          callAction={callAction}
          setRefetch={setRefetch}
        />
      )}
    </div>
  );
};

export default Rgb;
