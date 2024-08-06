import axios from "axios";
import React, { useContext, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ActiveHeat,
  ClimateErrorIcon,
  // ClimateWidgetHeatIcon,
  MinusIcon,
  PlusIcon,
} from "../../../assets/asset";
import { DataContext } from "../../../context/DataContext";
import styles from "./heat.module.css";

const DisplayText = React.memo(({ text, textColor, mounting }) => {
  const [animate, setAnimate] = useState(false);
  useEffect(() => {
    setAnimate((prev) => !prev);
  }, [text]);

  return (
    <div
      id="com-indoor"
      className={`${styles.desc} ${
        !mounting && (animate ? styles.animationText : styles.animationText2)
      }`}
      // style={{ color: textColor }}
    >
      {text}
    </div>
  );
});

const HeatMode = ({ data }) => {
  const { refreshParentData } = useContext(DataContext);
  const navigate = useNavigate();
  const btnClick = useRef(true);

  const redirect = () => {
    navigate(data?.actions[0]?.action?.href);
  };

  let textColor = "#8e8e93";
  if (data?.climateCurrentMode === "HEAT") {
    textColor = "#f15f31";
  }
  const changeTemp = async (type, e) => {
    btnClick.current = false;
    e.stopPropagation();
    if (type === "decrease") {
      await axios.put(data.actions[1].action.href, {
        mode: "HEAT",
        setTemp: data?.setTemp - 1,
      });
    } else if (type === "increase") {
      await axios.put(data.actions[2].action.href, {
        mode: "HEAT",
        setTemp: data?.setTemp + 1,
      });
    }
    refreshParentData();
  };

  return (
    <div id="com-temp" className={styles.container} onClick={redirect}>
      <div id="com-val" className={styles.mainTemp}>
        <span>
          {data?.climateCurrentMode === "ERROR" ? (
            <ClimateErrorIcon />
          ) : (
            <ActiveHeat />
          )}
        </span>
        <div className={styles.tempText}>
          {data?.interiorTempText}
          <span className={styles.middleSubText}>{data?.unit}</span>
        </div>
      </div>
      <DisplayText
        text={data?.climateModeSubtext}
        textColor={textColor}
        mounting={btnClick.current}
      />
      <div id="com-control" className={styles.controlBox}>
        <button
          id="com-btn"
          className={styles.controlButtons}
          style={{
            color: !data?.actions[1]?.active
              ? "var(--fills-surface-4)"
              : textColor,
            backgroundColor:
              !data?.actions[1]?.active && "var(--fills-surface-2)",
            border: !data?.actions[1]?.active && "none",
          }}
          disabled={!data?.actions[1]?.active}
          onClick={(e) => changeTemp("decrease", e)}
        >
          <MinusIcon />
        </button>
        <button
          id="com-btn1"
          className={styles.controlButtons}
          style={{
            color: !data?.actions[2]?.active
              ? "var(--fills-surface-4)"
              : textColor,
            backgroundColor:
              !data?.actions[2]?.active && "var(--fills-surface-2)",
            border: !data?.actions[2]?.active && "none",
          }}
          disabled={!data?.actions[2]?.active}
          onClick={(e) => changeTemp("increase", e)}
        >
          {" "}
          <PlusIcon />
        </button>
      </div>
    </div>
  );
};

export default HeatMode;
