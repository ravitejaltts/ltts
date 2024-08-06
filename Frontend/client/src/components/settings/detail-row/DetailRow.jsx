import axios from "axios";
import React from "react";
import { useNavigate } from "react-router-dom";
import { SelectedIcon, SettingArrow } from "../../../assets/asset";
import SimpleSwitch from "../../common/SimpleSwitch/SimpleSwitch";
import styles from "./index.module.css";

const DetailRow = ({
  icon,
  noBorder,
  arrow,
  text,
  name,
  selected,
  bottomText,
  toggle,
  toggleState,
  toggleAction,
  actionHref,
  buttonAction,
  type,
}) => {
  const navigate = useNavigate();

  function handleTextClick() {
    if (buttonAction) {
      axios.put(buttonAction.href);
    }
  }
  return (
    <>
      <div
        className={styles.row}
        onClick={() => actionHref && navigate(actionHref)}
      >
        <div>
          <div className={styles.nameIconContainer}>
            {icon && <span className={styles.icon}>{icon}</span>}
            {name}
          </div>
          {bottomText && (
            <>
              <span className={styles.bottomText}>{bottomText}</span>
            </>
          )}
        </div>

        {text && (
          <p className={styles.rightText} onClick={handleTextClick}>
            {text}
          </p>
        )}
        {arrow && <SettingArrow className={styles.settingArrow} />}
        {selected && <SelectedIcon className={styles.selectedArrow} />}
        {toggle && (
          <p className={styles.rightText}>
            <SimpleSwitch onOff={toggleState} toggleAction={toggleAction} />
          </p>
        )}
      </div>
      {!noBorder && <p className={styles.borderBottom}></p>}
    </>
  );
};

export default DetailRow;
