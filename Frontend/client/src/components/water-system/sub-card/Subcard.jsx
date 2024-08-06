import React from "react";
import SpeedIcon from "@mui/icons-material/Speed";
import styles from "./subcard.module.css";
const Subcard = () => {
  return (
    <div className={styles.container}>
      <SpeedIcon className={styles.icon} />
      <div>
        <p className={styles.text1}> Fresh Water</p>
        <p className={styles.text2}>
          {" "}
          About <span>3 Days</span> Remaining
        </p>
      </div>
    </div>
  );
};

export default Subcard;
