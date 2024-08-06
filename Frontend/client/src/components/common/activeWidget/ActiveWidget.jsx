import React from "react";
import { Link } from "react-router-dom";
import styles from "./active.module.css";

const ActiveWidget = (props) => {
  return (
    <Link to={props?.path} className={styles.activeLink}>
      <div className={styles.bottomWidget}>
        <div className={styles.whiteCircle}>{props.icon}</div>
        <p className={styles.content}>{props.text}</p>
      </div>
    </Link>
  );
};

export default ActiveWidget;
