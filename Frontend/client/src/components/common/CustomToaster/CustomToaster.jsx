import React from "react";
import { Close, ToastPlaceholder } from "../../../assets/asset";
import styles from "./index.module.css";

const CustomToaster = (props) => {
  const { icon, msg, closeToast, toastProps } = props;
  return (
    <div className={styles.container}>
      {icon ? (
        <div className={styles.icon}>{icon}</div>
      ) : (
        <div className={styles.icon}>
          <ToastPlaceholder />
        </div>
      )}
      <div className={styles.text}>{msg}</div>
      <Close
        onClick={() => closeToast(toastProps.toastId)}
        className={styles.closeBtn}
      />
    </div>
  );
};

export default CustomToaster;
