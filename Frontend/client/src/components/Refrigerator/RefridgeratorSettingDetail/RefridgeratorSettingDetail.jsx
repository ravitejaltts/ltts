import React from "react";
import { BackIcon } from "../../../assets/asset";
import RefridgeratorSettingRow from "../RefridgeratorSettingRow/RefridgeratorSettingRow";
import { MAIN_MODE } from "../RefrigeratorSettings/constants";
import styles from "./index.module.css";

const RefridgeratorSettingDetail = ({ data, setCurrentMode }) => {
  return (
    <div>
      <div className={styles.header}>
        <div className={styles.back} onClick={() => setCurrentMode(MAIN_MODE)}>
          <BackIcon />
          <h2>Back</h2>
        </div>
        <p className={styles.heading}>{data?.title}</p>
      </div>
      <div>
        <div className={styles.infoContainer}>
          {data?.items.map((section, ind, arr) => (
            <div key={ind}>
              <RefridgeratorSettingRow
                name={section.key}
                text={section.value}
                noBorder={ind === arr.length - 1}
              />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RefridgeratorSettingDetail;
