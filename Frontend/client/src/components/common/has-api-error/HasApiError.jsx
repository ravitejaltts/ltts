import React from "react";
import styles from "./error.module.css";
import Warning from "../../../assets/icons/notification/critical.png";

function HasApiError({ state }) {
  if (state) {
    return <img src={Warning} className={styles.errorIcon} />;
  } else {
    return null;
  }
}

export default HasApiError;
