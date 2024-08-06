import axios from "axios";
import React from "react";
import { toast } from "react-toastify";
import { useNavigate } from "react-router-dom";
import styles from "./active.module.css";
import CustomToaster from "../../common/CustomToaster/CustomToaster";
import useLongPress from "../../../hooks/useLongPress";

function ActiveWidget({ icon, data, color, refreshParentData = () => {} }) {
  const navigate = useNavigate();
  const onLongPress = () => {
    navigate(data?.action_longpress?.action?.href);
  };

  const onClick = () => {
    const alreadyActive = localStorage.getItem("alreadyActive");
    action(alreadyActive);
  };

  const defaultOptions = {
    shouldPreventDefault: true,
    delay: 500,
  };
  const longPressEvent = useLongPress(onLongPress, onClick, defaultOptions);

  const action = (alreadyActive) => {
    try {
      axios
        .put(data?.action_default?.action?.href, {
          onOff: data?.Simple?.onOff ? 0 : 1,
        })
        .then((res) => {
          if (res?.data?.msg?.msg && typeof res?.data?.msg?.msg === "string") {
            if (alreadyActive === "false" || alreadyActive === null) {
              toast(<CustomToaster msg={res?.data?.msg?.msg} icon={icon} />);
              localStorage.setItem("alreadyActive", "true");
              setTimeout(() => {
                localStorage.setItem("alreadyActive", "false");
              }, 3000);
            }
          }
          refreshParentData();
        });
    } catch (e) {
      console.log("error", e);
    }
  };

  return (
    <div id="com-active-widget" className={styles.bottomWidget} {...longPressEvent}>
      <div
        id="com-active-icon"
        className={`${styles.whiteCircle} ${
          data?.Simple?.onOff === 1 ? styles.active : styles.inactive
        } ${data?.Simple?.onOff === 1 ? color : styles.inactive}`}
        // style={{ backgroundColor: color }}
        // onClick={action}
      >
        {icon}
      </div>
      <div id="com-active-text" className={styles.content}>
        {data?.title}
      </div>
      <div className={styles.subText}>{data.subtext}</div>
    </div>
  );
}

export default ActiveWidget;
