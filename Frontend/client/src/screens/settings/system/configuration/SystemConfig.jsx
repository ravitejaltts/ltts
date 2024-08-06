import React from "react";
import SettingRow from "../../../../components/settings/setting-row/SettingRow";

import styles from "./config.module.css";

const SystemConfig = ({ data }) => {
  return (
    <>
      {data?.map((item, ind) => (
        <React.Fragment key={ind}>
          <div className={styles.itemContainer}>
            <p className={styles.containerHeading}>{item?.title}</p>
            <div className={styles.contentContainer}>
              {item?.data?.map((dat, ind, arr) => (
                <div key={ind}>
                  <SettingRow
                    name={dat?.title}
                    text={dat?.value}
                    toggle={dat?.Simple !== undefined}
                    toggleState={dat?.Simple?.onOff}
                    action={dat?.action_default?.action}
                    noBorder={arr.length - 1 === ind}
                    bottomText={dat?.subtext}
                  />
                </div>
              ))}
            </div>
          </div>
        </React.Fragment>
      ))}
    </>
  );
};

export default SystemConfig;
