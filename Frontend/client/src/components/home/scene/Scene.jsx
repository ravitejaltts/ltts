import React from "react";
import styles from "./scene.module.css";
import PlayCircleIcon from "@mui/icons-material/PlayCircle";

export const Scene = (props) => {
  return (
    <div id="com-scene" className={styles.container}>
      <div id="com-scene-icon" className={styles.icon}>
        <PlayCircleIcon />
      </div>
      <div id="com-scene" className={styles.contentBox}>
        <div id="com-scene-text" className={styles.header}>
          Scene
        </div>
        <div id="com-scene-text1" className={styles.text}>
          {props.text}
        </div>
      </div>
    </div>
  );
};
