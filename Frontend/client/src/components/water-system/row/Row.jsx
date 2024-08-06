import React, { useContext } from "react";
import { DataContext } from "../../../context/DataContext";
import styles from "./row.module.css";
import SwitchWithCustomParams from "../../common/SwitchWithCustomParams/SwitchWithCustomParams";

function Row({ title, subtext, icon, onOff, action, stylesExtra, params, disabled, type }) {
  const { refreshParentData = () => {} } = useContext(DataContext);
  return (
    <div className={`${styles.row} ${disabled ? styles.disabled : ""}`} style={{ ...stylesExtra }}>
      <div className={`${styles.rowLayout} ${!onOff && styles.disabledIcon}`}>
        {icon}
        <div className={styles.centerTextDiv}>
          <h2 className={styles.lightMasterText}>{title}</h2>
          <p className={styles.lightsOnText}>{subtext}</p>
        </div>
        <SwitchWithCustomParams
          onOff={onOff}
          action={action}
          refreshParentData={refreshParentData}
          params={params}
          disabled={disabled}
          type={type}
          subtext={subtext}
        />
      </div>
    </div>
  );
}

export default Row;
