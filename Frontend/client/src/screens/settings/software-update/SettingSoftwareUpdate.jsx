import React, { useEffect, useState } from "react";

import axios from "axios";
import { useLocation, useOutletContext } from "react-router-dom";
import SettingRow2 from "../../../components/settings/setting-row-2/SettingRow2";
import SettingRow3 from "../../../components/settings/setting-row-3/SettingRow3";
import UpdatingScreen from "../../../components/settings/updating-screen/UpdatingScreen";
import { SETTINGS_LINKS, UPDATE_SCREEN_VALUES } from "../../../constants/CONST";
import { DataContext } from "../../../context/DataContext";
import styles from "./update.module.css";
import AboutUpdate from "../../../components/settings/about-update-screen/AboutUpdate";
import UnableUpdate from "../../../components/settings/unable-update-screen/UnableUpdate";

const SettingSoftwareUpdate = () => {
  const location = useLocation();
  const [setActiveTab, data, refreshDataImmediate] = useOutletContext();
  useEffect(() => {
    setActiveTab(location?.pathname);
  }, []);
  const [displayFullScreenPage, setDisplayFullScreenPage] = useState("");
  const [infoData, setInfoData] = useState(null);

  const updateData = data?.[0]?.tabs?.find(
    (tab) => `${tab.name}` === SETTINGS_LINKS.SOFTWARE_UPDATE
  );
  function handleButtonMainClick(data) {
    if (data?.api_call?.href) {
      setInfoData(data);
      axios
        ?.put(data?.api_call?.href, {
          onOff: 1,
        })
        .then((res) => {
          if (res?.data?.status === "FAIL") {
            setDisplayFullScreenPage(UPDATE_SCREEN_VALUES.UPDATING_FAILED);
          }
          if (res?.data?.status === "OK") {
            setDisplayFullScreenPage(UPDATE_SCREEN_VALUES.UPDATING);
          }
        });
    }
    if (infoData?.api_call?.href) {
      axios
        ?.put(infoData?.api_call?.href, {
          onOff: 1,
        })
        .then((res) => {
          if (res?.data?.status === "FAIL") {
            setDisplayFullScreenPage(UPDATE_SCREEN_VALUES.UPDATING_FAILED);
          }
          if (res?.data?.status === "OK") {
            setDisplayFullScreenPage(UPDATE_SCREEN_VALUES.UPDATING);
          }
        });
    }
  }

  const handleButtonClick = (buttonData) => {
    if (buttonData?.action?.href) {
      axios.get(buttonData?.action?.href);
    }
    if (buttonData?.notes) {
      setInfoData(buttonData?.notes);
      setDisplayFullScreenPage(UPDATE_SCREEN_VALUES.ABOUT_UPDATE);
    }
    refreshDataImmediate();
  };

  function closeFullScreeen() {
    setDisplayFullScreenPage(false);
    setInfoData(null);
  }

  console.log(updateData, displayFullScreenPage);
  return (
    <DataContext.Provider
      value={{
        refreshParentData: refreshDataImmediate,
      }}
    >
      {displayFullScreenPage === UPDATE_SCREEN_VALUES.UPDATING && (
        <UpdatingScreen />
      )}
      {displayFullScreenPage === UPDATE_SCREEN_VALUES.UPDATING_FAILED && (
        <UnableUpdate
          close={closeFullScreeen}
          retryHandler={handleButtonMainClick}
        />
      )}
      {displayFullScreenPage === UPDATE_SCREEN_VALUES.ABOUT_UPDATE && (
        <AboutUpdate data={infoData} close={closeFullScreeen} />
      )}
      <div className={styles.header}>
        <p className={styles.headingText}>{updateData?.title}</p>
      </div>

      <div className={styles.itemContainer}>
        <div className={styles.contentContainer}>
          {updateData?.details?.data?.map((dat, ind, arr) => (
            <React.Fragment key={ind}>
              {dat?.type === "MULTI_NAVIGATION_BUTTON" && (
                <SettingRow2
                  name={dat?.title}
                  bottomText={dat?.subtitle}
                  buttonData={dat?.button}
                  noBorder={arr.length - 1 === ind}
                  handleButtonClick={handleButtonClick}
                />
              )}
              {dat?.type === "MULTI_NAVIGATION_BUTTON_PLUS" && (
                <SettingRow3
                  data={dat?.data}
                  noBorder={arr.length - 1 === ind}
                  handleButtonClick={handleButtonClick}
                  handleMainButtonClick={handleButtonMainClick}
                />
              )}
            </React.Fragment>
          ))}
        </div>
        <p className={styles.extraText}>
          The update process may take a few minutes to complete. Any systems
          currently running will be temporarily interrupted during the update
          process. Winnebago Connect will restart after the update is complete.
        </p>
      </div>
    </DataContext.Provider>
  );
};

export default SettingSoftwareUpdate;
