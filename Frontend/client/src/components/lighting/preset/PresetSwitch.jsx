import React, { useContext } from "react";
import axios from "axios";
import { toast } from "react-toastify";
import { DataContext } from "../../../context/DataContext";
import useLongPress from "../../../hooks/useLongPress";
import CustomToaster from "../../common/CustomToaster/CustomToaster";
import styles from "./preset.module.css";

function PresetSwitch({ data }) {
  const { refreshParentData = () => {} } = useContext(DataContext);
  const onLongPress = () => {
    axios.put(data?.action_longpress?.action?.href, data?.action_longpress?.action?.params).then(() => {
      refreshParentData();
    });
    // if (res?.data?.msg?.msg && typeof res?.data?.msg?.msg === "string") {
    // if (alreadyActive === "false" || alreadyActive === null) {
    toast.dismiss();
    toast(<CustomToaster msg={`Setting Preset ${data?.title}`} />);
    localStorage.setItem("alreadyActive", "true");
    setTimeout(() => {
      localStorage.setItem("alreadyActive", "false");
    }, 3000);
    // }
    // }
  };

  const onClick = () => {
    axios.put(data?.action?.action?.href, data?.action?.action?.params).then(() => {
      refreshParentData();
    });
  };

  const defaultOptions = {
    shouldPreventDefault: true,
    delay: 500,
  };
  const longPressEvent = useLongPress(onLongPress, onClick, defaultOptions);

  return (
    <div
      className={styles.presetSwitch}
      {...longPressEvent}
      //   onClick={() => callAction(data?.action?.action)}
    >
      <p
        className={styles.line}
        style={{
          backgroundColor: data?.Simple?.onOff ? "#0CA9DA" : "",
        }}
      ></p>
      <p className={styles.title}>{data?.title}</p>
      <p className={styles.switchText}>{data?.subtext}</p>
    </div>
  );
}

export default PresetSwitch;
