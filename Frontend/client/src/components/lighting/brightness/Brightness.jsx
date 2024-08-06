import React, { useCallback, useRef, useState } from "react";
import { debounce } from "../../../utils/utils";
import styles from "./brightness.module.css";

function Brightness({ data, callAction, setRefetch }) {
  const [level, setLevel] = useState(data?.brt);
  const mainBox = useRef();

  const maxLevel = data?.widget?.max;
  const minLevel = data?.widget?.min;
  const step = 5;

  function callParentAction(newLevel) {
    console.log(`Calling parent action, ${newLevel}`);
    callAction({ brt: newLevel });
  }

  const moveCapture = (e) => {
    e.stopPropagation();

    let newHeight =
      ((mainBox.current.getBoundingClientRect().bottom - e.changedTouches[0].clientY) /
        mainBox.current.getBoundingClientRect().height) *
      100;

    if (newHeight > 100) {
      newHeight = maxLevel;
    }

    if (newHeight < 5) {
      newHeight = minLevel;
    }

    newHeight -= newHeight % step;

    // Only send when the level has changed
    if (newHeight !== level) {
      callParentAction(newHeight);
      setLevel(newHeight);
    }
  };

  const incrementLevel = (stepper) => {
    setRefetch(false);

    let newLevel = level + stepper;

    if (newLevel > 100) {
      newLevel = maxLevel;
    }

    if (newLevel < 5) {
      newLevel = minLevel;
    }

    setLevel(newLevel);
  };

  const handleTouchStart = (e) => {
    e.stopPropagation();
    setRefetch(false);
  };

  const handleTouchEnd = (e) => {
    e.stopPropagation();
    optimisedActionCall(level);
  };

  const optimisedActionCall = useCallback(debounce(callParentAction, 500), []);

  return (
    <div brightness="" className={styles.container}>
      <div className={styles.title}>Brightness: {level}%</div>
      <div>
        <div
          className={styles.boxContainer}
          ref={mainBox}
          onTouchStart={handleTouchStart}
          onTouchMoveCapture={(e) => moveCapture(e)}
          onTouchEnd={handleTouchEnd}
          style={{ filter: !data?.state?.onOff ? "grayscale(1)" : "inherit" }}
          id="com-level-widget"
        >
          <div
            className={styles.colorFill}
            id="com-level-color"
            style={{
              height: `${level}%`,
              minHeight: "5%",
            }}
          >
            <span className={styles.whiteBar}></span>
          </div>
        </div>
      </div>
      <div className={styles.btnContainer}>
        {/* eslint-disable-next-line jsx-a11y/control-has-associated-label */}
        <button
          className={styles.btn1}
          type="button"
          onTouchStart={() => incrementLevel(-step)}
          onTouchEnd={handleTouchEnd}
        >
          <svg width="32" height="33" viewBox="0 0 32 33" fill="none" xmlns="http://www.w3.org/2000/svg">
            <g clipPath="url(#ddnobvcs4a)">
              <path
                d="M24.001 17.833h-16c-.733 0-1.333-.6-1.333-1.334 0-.733.6-1.333 1.333-1.333h16c.734 0 1.334.6 1.334 1.333 0 .734-.6 1.334-1.334 1.334z"
                fill="#404045"
              />
            </g>
            <defs>
              <clipPath id="ddnobvcs4a">
                <path fill="#fff" transform="translate(0 .5)" d="M0 0h32v32H0z" />
              </clipPath>
            </defs>
          </svg>
        </button>
        {/* eslint-disable-next-line jsx-a11y/control-has-associated-label */}
        <button
          className={styles.btn2}
          type="button"
          onTouchStart={() => incrementLevel(+step)}
          onTouchEnd={handleTouchEnd}
        >
          <svg width="32" height="33" viewBox="0 0 32 33" fill="none" xmlns="http://www.w3.org/2000/svg">
            <g clipPath="url(#ld9wt9zvsa)">
              <path
                d="M24.001 17.833h-6.666v6.666c0 .734-.6 1.334-1.334 1.334-.733 0-1.333-.6-1.333-1.334v-6.666H8.001c-.733 0-1.333-.6-1.333-1.334 0-.733.6-1.333 1.333-1.333h6.667V8.499c0-.733.6-1.333 1.333-1.333.734 0 1.334.6 1.334 1.333v6.667H24c.734 0 1.334.6 1.334 1.333 0 .734-.6 1.334-1.334 1.334z"
                fill="#404045"
              />
            </g>
            <defs>
              <clipPath id="ld9wt9zvsa">
                <path fill="#fff" transform="translate(0 .5)" d="M0 0h32v32H0z" />
              </clipPath>
            </defs>
          </svg>
        </button>
      </div>
    </div>
  );
}

export default Brightness;
