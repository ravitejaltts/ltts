import React from "react";
import { SelectedIcon, SettingArrow } from "../../../assets/asset";
import styles from "./index.module.css";

const RefridgeratorSettingRow = ({ noBorder, arrow, text, name, selected }) => {
  return (
    <>
      <div className={styles.row}>
        <span>{name}</span>
        {text && <p className={styles.rightText}>{text}</p>}
        {arrow && <SettingArrow className={styles.settingArrow} />}
        {selected && <SelectedIcon className={styles.selectedArrow} />}
      </div>
      {!noBorder && <p className={styles.borderBottom}></p>}
    </>
  );
};

export default RefridgeratorSettingRow;
