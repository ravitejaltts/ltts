import React, { useState } from "react";
import styles from "./watertemp.module.css";
import AddIcon from "@mui/icons-material/Add";
import RemoveIcon from "@mui/icons-material/Remove";
const WaterTemp = () => {
  const [value, setvalue] = useState(110);
  return (
    <div className={styles.container}>
      <div className={styles.title}>Water Temp</div>
      <div className={styles.controlBox}>
        <div
          className={styles.decrease}
          onClick={() => setvalue((prev) => prev - 1)}
        >
          <RemoveIcon fontSize="large" />
        </div>
        <div className={styles.temperature}>{value}</div>
        <div
          className={styles.increase}
          onClick={() => setvalue((prev) => prev + 1)}
        >
          <AddIcon fontSize="large" />
        </div>
      </div>
    </div>
  );
};

export default WaterTemp;
