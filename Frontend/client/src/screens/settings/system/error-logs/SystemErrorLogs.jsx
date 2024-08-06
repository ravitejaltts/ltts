import React from "react";
import styles from "./index.module.css";
import SystemErrorCard from "../../../../components/settings/error-card/SystemErrorCard";

const SystemErrorLogs = ({ data }) => {
  return (
    <div className={styles.container}>
      {data?.map((error , i) => (
        <SystemErrorCard data={error} key={i} />
      ))}
    </div>
  );
};

export default SystemErrorLogs;
