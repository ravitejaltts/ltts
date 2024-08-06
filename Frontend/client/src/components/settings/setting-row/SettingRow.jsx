import axios from "axios";
import React from "react";
import { SelectedIcon, SettingArrow } from "../../../assets/asset";
import SimpleSwitch from "../../common/SimpleSwitch/SimpleSwitch";
import styles from "./row.module.css";

const SettingRow = ({
  noBorder,
  arrow,
  text,
  name,
  selected,
  bottomText,
  toggle,
  toggleState,
  value,
  action,
  refreshDataImmediate,
}) => {
  const handleOnClick = async () => {
    if (action && !toggle) {
      await axios.put(action.href, {
        value,
        item: action?.params?.item,
      });
      refreshDataImmediate();
    }
  };
  return (
    <>
      <div
        className={styles.row}
        style={{ padding: bottomText && "5px 16px" }}
        onClick={handleOnClick}
      >
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
            <SimpleSwitch
              refreshDataImmediate={refreshDataImmediate}
              onOff={toggleState}
              toggleAction={action}
            />
          </p>
        )}
      </div>
      {!noBorder && <p className={styles.borderBottom}></p>}
    </>
  );
};

export default SettingRow;
