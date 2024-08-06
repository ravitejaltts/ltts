import React from "react";
import styles from "./helper.module.css";

export const IconBoxSquare = ({ icon }) => {
  return <div className={styles.squareContainer}>{icon}</div>;
};

export const IconBoxCircle = ({ icon }) => {
  return <div className={styles.circleContainer}>{icon}</div>;
};
