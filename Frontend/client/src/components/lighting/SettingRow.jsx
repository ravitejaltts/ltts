import React from "react";
import { SelectedIcon, SettingArrow } from "../../assets/asset";
import { TrumaLogo } from "../../assets/asset";
import SimpleSwitch from "../common/SimpleSwitch/SimpleSwitch";
import styles from "./row.module.css";

const SettingRow = ({
  noBorder,
  arrow,
  text,
  name,
  selected,
  bottomText,
  toggle,
}) => {
  return (
    <>
      <div className={styles.row}>
        <div>
          {name}{" "}
          {bottomText && (
            <>
              <br />
              <span className={styles.bottomText}>{bottomText}</span>
            </>
          )}
        </div>

        {text && <p className={styles.rightText}>{text}</p>}
        {arrow && <SettingArrow className={styles.settingArrow} />}
        {selected && <SelectedIcon className={styles.selectedArrow} />}
        {toggle && (
          <p className={styles.rightText}>
            <SimpleSwitch />
          </p>
        )}
      </div>
      {!noBorder && <p className={styles.borderBottom}></p>}
    </>
  );
};

export default SettingRow;
