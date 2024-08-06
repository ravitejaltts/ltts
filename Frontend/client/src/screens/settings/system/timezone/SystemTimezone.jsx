import axios from "axios";
import React, { useContext } from "react";
import SettingRow from "../../../../components/settings/setting-row/SettingRow";
import styles from "./timezone.module.css";
import { DataContext } from "../../../../context/DataContext";

const SystemTimezone = ({ data }) => {
  const { refreshParentData } = useContext(DataContext);
  const handleClick = (dat, val) => {
    axios
      .put(dat?.actions?.TAP?.action?.href, {
        value: val?.key,
        item: "TimeZonePreference",
      })
      .then(() => {
        refreshParentData();
      });
  };
  return (
    <>
      {data?.data?.map((item, ind) => (
        <React.Fragment key={ind}>
          <div className={styles.itemContainer}>
            <p className={styles.containerHeading}>{item?.title}</p>
            <div className={styles.contentContainer}>
              {item?.options?.map((dat, ind, arr) => (
                <div key={ind} onClick={() => handleClick(item, dat)}>
                  <SettingRow
                    name={dat?.key}
                    selected={dat?.selected}
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

export default SystemTimezone;
