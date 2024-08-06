import axios from "axios";
import React from "react";
import styles from "../../style/switch.module.css";

function Switch({ onOff, action, noPayload, refreshParentData = () => {} }) {
  const onSwitchChange = (e) => {
    // console.log(e)
    e.stopPropagation();
  };
  const callAction = () => {
    // console.log('Switch action', action)
    axios
      .put(
        action?.href,
        !noPayload && {
          onOff: onOff ? 0 : 1,
        },
      )
      .catch((err) => console.error(err))
      .finally(() => {
        refreshParentData();
      });
  };

  return (
    <input
      switch=""
      type="checkbox"
      className={styles.switch}
      // defaultChecked={!!onOff}
      checked={!!onOff}
      onChange={onSwitchChange}
      onTouchStart={callAction}
    ></input>
  );
}

export default Switch;
