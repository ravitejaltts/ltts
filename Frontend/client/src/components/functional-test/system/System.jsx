import React from "react";
import { FreshTankLevel, GreyTankLevel } from "../../../assets/asset";
import styles from "./system.module.css";

const iconObj = {
  FreshTankLevel: <FreshTankLevel />,
  GreyTankLevel: <GreyTankLevel />,
};

const System = ({ data }) => {
  return (
    <div className={styles.system}>
      <div
        className={styles.top}
        style={{ backgroundColor: data?.color_empty }}
      >
        <div className={styles.icon}>{iconObj[data?.name]}</div>
        <div className={styles.levelText}>{data?.simpleLevel.level_text}</div>
        <div
          className={styles.colorFill}
          style={{
            height: `${data?.simpleLevel?.current_value}%`,
            backgroundColor: data?.color_fill,
          }}
        ></div>
      </div>
      <div className={styles.bottom}>
        <p className={styles.title}>{data?.title}</p>
        <p className={styles.subText}>{data?.subtext}</p>
      </div>
    </div>
  );
};

export default System;
