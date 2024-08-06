import React from "react";
import Switch from "../../common/switch/Switch";
import styles from "./row.module.css";

const Row = ({ title, subtext, icon, onOff, action }) => {
  return (
    <div className={styles.row}>
      <div className={styles.rightTop}>
        {icon}
        <div className={styles.centerTextDiv}>
          <h2 className={styles.lightMasterText}>{title}</h2>
          <p className={styles.lightsOnText}>{subtext}</p>
        </div>
        <Switch onOff={onOff} action={action} />
      </div>
    </div>
  );
};

export default Row;
