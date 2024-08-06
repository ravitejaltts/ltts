import React from "react";
import { useNavigate } from "react-router-dom";
import { ClimateErrorIcon, ClimateWidgetIcon } from "../../../assets/asset";
import styles from "./auto.module.css";
// auto
const AutoMode = ({ data }) => {
  const navigate = useNavigate();

  const redirect = () => {
    navigate(data?.actions[0]?.action?.href);
  };

  let bottomTextColor = "#8e8e93";
  if (data?.climateCurrentMode === "COOL") {
    bottomTextColor = "#0ca9da";
  } else if (data?.climateCurrentMode === "HEAT") {
    bottomTextColor = "#f15f31";
  }

  return (
    <div id="com-temp" className={styles.container} onClick={redirect}>
      <h2 className={styles.autoHeading}>Auto Mode</h2>
      <div id="com-val" className={styles.mainTemp}>
        <span>
          {data?.climateCurrentMode === "ERROR" ? (
            <ClimateErrorIcon />
          ) : (
            <ClimateWidgetIcon />
          )}
        </span>
        <div className={styles.tempText}>
          {data?.interiorTempText}
          <span className={styles.middleSubText}>{data?.unit}</span>
        </div>
      </div>
      <div className={styles.bottomText} style={{ color: bottomTextColor }}>
        {data?.climateModeSubtext}
      </div>
    </div>
  );
};

export default AutoMode;
