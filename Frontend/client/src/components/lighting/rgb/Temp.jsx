import React, { useRef, useState } from "react";
import styles from "./temp.module.css";

const Temp = ({ data, setData, callAction, setRefetch }) => {
  const defaultLevel = (data?.clrTmp - 3000) / 60 || 50;
  const [level, setLevel] = useState(defaultLevel);
  const mainBox = useRef();
  const drag = useRef(false);

  // setTimeout(() => {}, [1000]);

  const getColorFromLevel = (value) => {
    if (value >= 0 && value < 20) {
      return "#d5feff";
    }
    if (value >= 20 && value < 40) {
      return "#edfff1";
    }
    if (value >= 40 && value < 60) {
      return "#fbffec";
    }
    if (value >= 60 && value < 80) {
      return "#fef5b3";
    }
    if (value >= 80 && value <= 100) {
      return "#ffd97f";
    }
  };

  const moveCapture = (e) => {
    drag.current = true;
    e.stopPropagation();

    let newHeight =
      ((mainBox.current.getBoundingClientRect().bottom -
        e.changedTouches[0].clientY) /
        mainBox.current.getBoundingClientRect().height) *
      100;
    if (newHeight > 100) {
      newHeight = 100;
    }
    if (newHeight < 0) {
      newHeight = 0;
    }
    if (newHeight > 100) {
      newHeight = 100;
    }
    newHeight = parseInt(newHeight);
    setLevel(newHeight);
    setData((prev) => {
      return {
        ...prev,
        clrTmp: Math.floor(Number(newHeight) * 60 + 3000),
        rgb: getColorFromLevel(newHeight),
      };
    });
  };

  const handleTouchStart = (e) => {
    e.stopPropagation();
    setRefetch(false);
  };
  const handleTouchEnd = (e) => {
    e.stopPropagation();
    if (drag.current) {
      callAction({
        clrTmp: Math.floor(Number(level) * 60 + 3000),
        rgb: getColorFromLevel(level),
      });
    }
    drag.current = false;
  };
  const handleClick = (e, color) => {
    e.stopPropagation();

    setData((prev) => {
      return {
        ...prev,
        rgb: getColorFromLevel(level),
      };
    });

    callAction({
      clrTmp: Math.floor(Number(level) * 60 + 3000),
      rgb: getColorFromLevel(level),
    });
  };

  return (
    <>
      <div className={styles.mainCircle}>
        <div
          className={styles.innerVerticalContainer}
          ref={mainBox}
          onTouchStart={handleTouchStart}
          onTouchMoveCapture={(e) => moveCapture(e)}
          onTouchEnd={handleTouchEnd}
        >
          <div style={{ bottom: level + "%" }} className={styles.circle}></div>
        </div>

        <div
          className={styles.colorFill}
          id="com-level-color"
          style={{ backgroundColor: "red", height: `${level}%` }}
        >
          {/* <span className={styles.whiteBar}></span> */}
        </div>
      </div>
      <div className={styles.sampleBox}>
        <div
          className={styles.sample}
          style={{ background: "#ffd97f" }}
          onTouchStart={() => setLevel(100)}
          onTouchEnd={(e) => handleClick(e, "#ffd97f")}
        ></div>
        <div
          className={styles.sample}
          style={{ background: "#fef5b3" }}
          onTouchStart={() => setLevel(75)}
          onTouchEnd={(e) => handleClick(e, "#fef5b3")}
        ></div>
        <div
          className={styles.sample}
          style={{ background: "#fbffec" }}
          onTouchStart={() => setLevel(50)}
          onTouchEnd={(e) => handleClick(e, "#fbffec")}
        ></div>
        <div
          className={styles.sample}
          style={{ background: "#edfff1" }}
          onTouchStart={() => setLevel(25)}
          onTouchEnd={(e) => handleClick(e, "#edfff1")}
        ></div>
        <div
          className={styles.sample}
          style={{ background: "#d5feff" }}
          onTouchStart={() => setLevel(0)}
          onTouchEnd={(e) => handleClick(e, "#d5feff")}
        ></div>
      </div>
    </>
  );
};

export default Temp;
