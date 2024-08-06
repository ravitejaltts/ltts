import axios from "axios";
import React, { useEffect } from "react";
import { useLocation, useOutletContext } from "react-router-dom";
import SettingRow from "../../../components/settings/setting-row/SettingRow";
import { SETTINGS_LINKS } from "../../../constants/CONST";
import styles from "./revel.module.css";

const SettingRevel = () => {
  const location = useLocation();
  const [setActiveTab, data] = useOutletContext();

  const revelData = data?.[0]?.tabs?.filter((tab) => `${tab.name}` === SETTINGS_LINKS.REVEL)[0]?.details;

  useEffect(() => {
    setActiveTab(location?.pathname);
  }, []);

  const rebootApiCall = async () => {
    axios
      .put("/api/system/reboot")
      .then((res) => {
        // success callback
      })
      .catch((err) => {
        console.error(err);
      });
  };

  return (
    <div>
      <div className={styles.header}>
        <p className={styles.headingText}>{revelData?.title}</p>
      </div>
      {revelData?.data?.map((item, ind) => (
        <React.Fragment key={ind}>
          <div className={styles.itemContainer}>
            <p className={styles.containerHeading}>{item.title}</p>
            <div className={styles.contentContainer}>
              {item?.items?.map((dat, ind, arr) => (
                <React.Fragment key={ind}>
                  <SettingRow
                    name={dat?.title}
                    text={dat?.value?.version || dat?.value}
                    noBorder={arr.length - 1 === ind}
                    bottomText={dat?.subtext?.version}
                  />
                </React.Fragment>
              ))}
            </div>
          </div>
        </React.Fragment>
      ))}
      {/* <button className={styles.resetBtn} onClick={rebootApiCall}>
        Reboot
      </button> */}
    </div>
  );
};

export default SettingRevel;
