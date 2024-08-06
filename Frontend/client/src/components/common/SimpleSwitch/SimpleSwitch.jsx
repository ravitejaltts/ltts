import axios from "axios";
import React from "react";
import styles from "../../style/switch.module.css";

const SimpleSwitch = (
  {
    onOff,
    toggleAction,
    extraPayload,
    refreshDataImmediate,
  }) => {
  function handleChange(e) {
    e.cancelBubble = true;
    e.stopPropagation();
    const state = Number(e.target.checked);
    axios
      .put(toggleAction.href, {
        ...(toggleAction?.params?.item && {item: toggleAction?.params?.item}),
        ...extraPayload,
        onOff: state,
      })
      .then(() => {
        if (refreshDataImmediate) {
          refreshDataImmediate();
        }
      });
  }

  return (
    <>
      <input
        simpleswitch=""
        type="checkbox"
        className={styles.switch}
        checked={onOff}
        onChange={handleChange}
      ></input>
    </>
  );
};

export default SimpleSwitch;
