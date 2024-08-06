import React from "react";
import SettingRow from "../../../../components/settings/setting-row/SettingRow";

import styles from "./location.module.css";

const SystemLocation = ({ data }) => {
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
                    toggle
                    toggleState={dat?.Simple?.onOff}
                    action={dat?.actions?.TOGGLE?.action}
                    noBorder={arr.length - 1 === ind}
                    bottomText={dat?.subtext}
                  />
                </div>
              ))}
            </div>
          </div>
        </React.Fragment>
      ))}
      <p className={styles.info}>{data[0]?.data?.[0]?.belowtext}</p>
    </>
  );
};

export default SystemLocation;
