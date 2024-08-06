import axios from "axios";
import React from "react";
import styles from "./index.module.css";

const Button = ({ action, text, refreshParentData = () => {} }) => {
  const callAction = () => {
    axios
      .put(action?.href)
      .then((res) => {
        refreshParentData();
      })
      .catch((err) => console.error(err));
  };
  return (
    <button className={styles.button} onClick={action ? callAction : null}>
      {text}
    </button>
  );
};

export default Button;
