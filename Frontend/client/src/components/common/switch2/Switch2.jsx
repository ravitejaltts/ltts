import React from "react";
import styles from "../../style/switch.module.css";

// Switch 2 doesn't call action api like 1 it provides value of onOff and calls the function provided as action
const Switch2 = ({onOff, action, roofFan}) => {
  const callAction = () => {
    if (roofFan) {
      return action(Number(!onOff), roofFan);
    } else {
      action(Number(!onOff));
    }
  };

  return (
    <>
      <input
        switch2=""
        type="checkbox"
        className={styles.switch}
        checked={!!onOff}
        onChange={callAction}
      ></input>
    </>
  );
};

export default Switch2;
