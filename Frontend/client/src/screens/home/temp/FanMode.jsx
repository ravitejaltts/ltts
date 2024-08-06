import axios from "axios";
import { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../../../context/AppContext";
import {
  ClimateBlackFanIcon,
  ClimateErrorIcon,
  ClimateFanOffIcon,
} from "../../../assets/asset";
import { DataContext } from "../../../context/DataContext";
import styles from "./fan.module.css";

const FanMode = ({ data }) => {
  const { refreshParentData } = useContext(DataContext);
  const { animate } = useContext(AppContext);
  const navigate = useNavigate();

  const redirect = () => {
    navigate(data?.actions[0]?.action?.href);
  };
  const changeFanSpeed = async (type, e) => {
    e.stopPropagation();
    if (type === "decrease") {
      await axios
        .put(data.actions[1].action.href, {
          ...data?.actions[1]?.action?.params,
        })
        .finally(() => {});
    } else if (type === "increase") {
      await axios.put(data.actions[2].action.href, {
        ...data?.actions[2]?.action?.params,
      });
    }
    refreshParentData();
  };
  let textColor = "#000000";
  return (
    <div id="com-temp" className={styles.container} onClick={redirect}>
      <div id="com-val" className={styles.mainTemp}>
        <span>
          {data?.fanState[0].active === 0 && (
            <span className={styles.fanIcon}>
              <ClimateFanOffIcon />
            </span>
          )}
          {data?.climateCurrentMode === "ERROR" && (
            <span className={styles.fanIcon}>
              <ClimateErrorIcon />
            </span>
          )}
          {data?.fanState[0].active === 1 && (
            <span
              className={`${styles.animationIcon} ${
                animate && styles.animate
              } ${
                animate && !data.actions[2]?.active && styles.fasterAnimation
              } `}
            >
              <ClimateBlackFanIcon />
            </span>
          )}
        </span>
        <div className={styles.tempText}>
          <span>{data?.interiorTempText}</span>
          <span className={styles.middleSubText}>{data?.unit}</span>
        </div>
      </div>
      <div id="com-indoor" className={styles.desc}>
        {data?.climateModeSubtext}
      </div>
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
          onClick={(e) => changeFanSpeed("decrease", e)}
        >
          <svg width="32" height="33" viewBox="0 0 32 33" fill="none" xmlns="http://www.w3.org/2000/svg">
              <g clipPath="url(#ddnobvcs4a)">
                  <path d="M24.001 17.833h-16c-.733 0-1.333-.6-1.333-1.334 0-.733.6-1.333 1.333-1.333h16c.734 0 1.334.6 1.334 1.333 0 .734-.6 1.334-1.334 1.334z" fill="#404045"/>
              </g>
              <defs>
                  <clipPath id="ddnobvcs4a">
                      <path fill="#fff" transform="translate(0 .5)" d="M0 0h32v32H0z"/>
                  </clipPath>
              </defs>
          </svg>
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
          onClick={(e) => changeFanSpeed("increase", e)}
        >
          {/* {" "} */}
          <svg width="32" height="33" viewBox="0 0 32 33" fill="none" xmlns="http://www.w3.org/2000/svg">
              <g clipPath="url(#ld9wt9zvsa)">
                  <path d="M24.001 17.833h-6.666v6.666c0 .734-.6 1.334-1.334 1.334-.733 0-1.333-.6-1.333-1.334v-6.666H8.001c-.733 0-1.333-.6-1.333-1.334 0-.733.6-1.333 1.333-1.333h6.667V8.499c0-.733.6-1.333 1.333-1.333.734 0 1.334.6 1.334 1.333v6.667H24c.734 0 1.334.6 1.334 1.333 0 .734-.6 1.334-1.334 1.334z" fill="#404045"/>
              </g>
              <defs>
                  <clipPath id="ld9wt9zvsa">
                      <path fill="#fff" transform="translate(0 .5)" d="M0 0h32v32H0z"/>
                  </clipPath>
              </defs>
          </svg>
        </button>
      </div>
    </div>
  );
};

export default FanMode;
