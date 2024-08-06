import axios from "axios";
import React from "react";
import { toast } from "react-toastify";
import CustomToaster from "../CustomToaster/CustomToaster";
import { WavesIcon } from "../../../assets/asset";
import styles from "../../style/switch.module.css";

function SwitchWithCustomParams({
  onOff,
  action,
  noPayload,
  refreshParentData = () => {},
  params,
  disabled,
  type,
}) {
  const toggleSwitchWithCustomParams = () => {
    if (disabled) return;
    axios
      .put(action?.href, !noPayload && params)
      .then(() => {
        if (onOff && type === "TANKPAD") {
          toast(
            <CustomToaster
              msg="Turning off Heating Pads could allow tank contents to freeze."
              icon={<WavesIcon />}
            />,
          );
        }
        refreshParentData();
      })
      .catch((err) => console.error(err));
  };

  return (
    <input
      switchwithcustomparams=""
      type="checkbox"
      className={styles.switch}
      defaultChecked={!!onOff}
      // checked={!!onOff}
      onTouchStart={toggleSwitchWithCustomParams}
    ></input>
  );
}

export default SwitchWithCustomParams;
