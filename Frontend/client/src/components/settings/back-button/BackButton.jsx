import React from "react";
import { BackIcon } from "../../../assets/asset";
import styles from "./back.module.css";

function BackButton({ handler }) {
  return (
    <div>
      <div className={styles.container} onClick={handler}>
        <BackIcon />
        Back
      </div>
    </div>
  );
}

export default BackButton;
