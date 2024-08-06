import React from "react";
import styles from "./index.module.css";

const SystemErrorCard = ({ data }) => {
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div>
          <p className={styles.topText}>{data?.topText}</p>

          <span className={styles.title}>{data?.title}</span>
        </div>
        <span className={styles.timeStamp}>{data?.timestamp}</span>
      </div>
      <p className={styles.body}>{data?.body}</p>
    </div>
  );
};

export default SystemErrorCard;
