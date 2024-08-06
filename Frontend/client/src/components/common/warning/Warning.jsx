import WarningAmberRoundedIcon from "@mui/icons-material/WarningAmberRounded";
import React from "react";
import styles from "./warning.module.css";

const Warning = () => {
  return (
    <div className={styles.mainBox}>
      <div>
        <div className={styles.iconContainer}>
          <WarningAmberRoundedIcon
            className={styles.hazard}
            htmlColor="black"
          />
          <div className={styles.iconText}>Hazard Warning</div>
        </div>
        <div className={styles.mainHeading}>
          Be Aware of your surroundings while operating
        </div>
        <div className={styles.content}>
          {" "}
          Before operating,ensure are is free from people and objects.Failure to
          comply could result in severe injury and/or property damage.
        </div>
      </div>
      <div className={styles.bottomBar}>
        <div className={styles.checkBoxContainer}>
          <input type="checkbox" id="check" className={styles.checkBox} />
          <label for="check">Don't ask again</label>
        </div>
        <div className={styles.btnBox}>
          <button>Cancel</button>
          <button>Acknowledge</button>
        </div>
      </div>
    </div>
  );
};

export default Warning;
