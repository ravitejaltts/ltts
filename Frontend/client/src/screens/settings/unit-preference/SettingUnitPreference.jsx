import React, { useEffect } from "react";

import { useLocation, useOutletContext } from "react-router-dom";
import SettingRow from "../../../components/settings/setting-row/SettingRow";
import { SETTINGS_LINKS } from "../../../constants/CONST";
import styles from "./unit.module.css";

const SettingUnitPreference = () => {
  const location = useLocation();
  const [setActiveTab, data , refreshDataImmediate] = useOutletContext();
  useEffect(() => {
    setActiveTab(location?.pathname);
  }, []);

  const unitPreferenceData = data?.[0]?.tabs?.filter(
    (tab) => `${tab.name}` === SETTINGS_LINKS.UNIT_PREFERENCES
  )[0];
  return (
    <>
      <div className={styles.header}>
        <p className={styles.headingText}>{unitPreferenceData?.title}</p>
      </div>
      {unitPreferenceData?.details?.data?.map((item, ind) => (
        <React.Fragment key={ind}>
          <div className={styles.itemContainer}>
            <p className={styles.containerHeading}>{item.title}</p>
            <div className={styles.contentContainer}>
              {item?.options?.map((dat, ind, arr) => (
                <React.Fragment key={ind}>
                  <SettingRow
                    name={dat?.key}
                    selected={dat?.selected}
                    value={dat?.value}
                    noBorder={arr.length - 1 === ind}
                    bottomText={dat?.subtext}
                    action={item?.actions?.TAP?.action}
                    refreshDataImmediate={refreshDataImmediate}
                  />
                </React.Fragment>
              ))}
            </div>
          </div>
        </React.Fragment>
      ))}
    </>
  );
};

export default SettingUnitPreference;
