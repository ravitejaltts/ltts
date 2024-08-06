import React, { useEffect } from "react";
import SettingRow from "../../../components/settings/setting-row/SettingRow";
import { SETTINGS_LINKS } from "../../../constants/CONST";
import styles from "./notification.module.css";
import { useLocation, useOutletContext } from "react-router-dom";

const SettingNotification = () => {
  const location = useLocation();
  const [setActiveTab, data, refreshDataImmediate] = useOutletContext();

  const notificationData = data?.[0]?.tabs?.filter(
    (tab) => `${tab.name}` === SETTINGS_LINKS.NOTIFICATIONS
  )[0];

  useEffect(() => {
    setActiveTab(location?.pathname);
  }, []);

  return (
    <>
      <div className={styles.header}>
        <p className={styles.headingText}>{notificationData?.title}</p>
      </div>
      <div className={styles.itemContainer}>
        <div className={styles.contentContainer}>
          {notificationData?.details?.data[0]?.items?.map((dat, ind, arr) => (
            <React.Fragment key={ind}>
              {dat?.type === "SIMPLE_ONOFF" ? (
                <SettingRow
                  name={dat?.title}
                  toggle
                  text={dat?.state?.onoff ? "On" : "Off"}
                  toggleState={dat?.state?.onoff}
                  noBorder={arr.length - 1 === ind}
                  action={dat?.actions?.TOGGLE?.action}
                  refreshDataImmediate={refreshDataImmediate}
                />
              ) : (
                <SettingRow
                  name={dat?.title}
                  arrow
                  text={dat?.value?.version || dat?.value}
                  noBorder={arr.length - 1 === ind}
                  bottomText={dat?.subtext}
                />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    </>
  );
};

export default SettingNotification;
