import React from "react";
import Switch from "../../common/switch/Switch";
import { icons } from "../../constants/icons/Icons";
import styles from "./smallcard.module.css";

const SmallCard = () => {
  return (
    <div className={styles.container}>
      <div className={styles.icon}>{icons["Water Pump"]}</div>
      <div className={styles.title}>Water Pump</div>
      {/* <div className={styles.switch}>
        <Switch />
      </div> */}
    </div>
  );
};

export default SmallCard;
