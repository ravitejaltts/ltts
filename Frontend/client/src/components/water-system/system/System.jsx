import React from "react";
import { BlackTankLevel, FreshTankLevel, GreyTankLevel } from "../../../assets/asset";
import styles from "./system.module.css";
import { PropaneCylinerIcon } from "../../../assets/assets";

const iconObj = {
  FreshTankLevel: <FreshTankLevel />,
  GreyTankLevel: <GreyTankLevel />,
  BlackTankLevel: <BlackTankLevel />,
  PropaneTankLevel: <PropaneCylinerIcon />,
};

function System({ data, borderColor, classNames }) {
  return (
    <div system="" className={styles.system} style={{ borderColor }}>
      <div className={styles.top} style={{ backgroundColor: data?.color_empty }}>
        <div className={styles.icon}>
          {iconObj[data?.name] ? iconObj[data?.name] : <FreshTankLevel />}
          {/* FreshTankLevel is default icon... */}
        </div>
        <div className={styles.levelText}>{data?.state?.level_text}</div>
        <div
          className={`${styles.colorFill} ${classNames}`}
          style={{
            height: `${data?.state?.current_value}%`,
            backgroundColor: data?.color_fill,
          }}
        ></div>
      </div>
      <div className={styles.bottom}>
        <div className={styles.title}>
          {" "}
          {data?.title?.split(" ")?.map((word, ind) => (
            <p className="m-0" key={ind}>
              {word}
            </p>
          ))}
        </div>
        <p className={styles.subText}>{data?.subtext}</p>
      </div>
    </div>
  );
}

export default System;
