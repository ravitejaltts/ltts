import axios from "axios";
import React, { useCallback, useRef, useState } from "react";
import { debounce } from "../../../utils/utils";
import styles from "./slider.module.css";

function AwningSlider({ data }) {
  const [level, setLevel] = useState(data?.state?.brt || 0);
  const mainBox = useRef();

  const maxLevel = data?.widget?.max;
  const minLevel = data?.widget?.min;
  const step = data?.widget?.step;

  function callParentAction(newLevel) {
    if (data?.action_default?.action?.href) {
      axios.put(data?.action_default?.action?.href, {
        // ...data.state,
        brt: newLevel,
      });
    }
  }

  const moveCapture = (e) => {
    e.stopPropagation();

    let newHeight =
      ((e.changedTouches[0].clientX - mainBox.current.getBoundingClientRect().left) /
        mainBox.current.getBoundingClientRect().width) *
      100;

    if (newHeight > 100) {
      newHeight = maxLevel;
    }

    if (newHeight < 0) {
      newHeight = minLevel;
    }

    newHeight -= newHeight % step;

    setLevel(newHeight);
  };

  const handleTouchStart = (e) => {
    e.stopPropagation();
  };

  const handleTouchEnd = (e) => {
    e.stopPropagation();
    optimisedActionCall(level);
  };

  const optimisedActionCall = useCallback(debounce(callParentAction, 1000), []);

  return (
    <div className={styles.container}>
      {!data?.state?.onOff && <div className={styles.overlay} />}
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
            width: `${level}%`,
            minWidth: "5%",
          }}
        >
          <span className={styles.whiteBar}></span>
        </div>
      </div>
    </div>
  );
}

export default AwningSlider;
