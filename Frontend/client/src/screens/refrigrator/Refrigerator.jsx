import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../../context/AppContext";
import { BackIcon, FridgeIcon, SettingsIcon } from "../../assets/asset";
import Popup from "../../components/common/Popup/Popup";
import RefrigeratorSettings from "../../components/Refrigerator/RefrigeratorSettings";
import { DataContext } from "../../context/DataContext";
import { useFetch } from "../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../utils/api";
import { REFRIDGERATOR_TITLE } from "./constants";
import styles from "./refrigerator.module.css";
import LeftBottomTwoWidgets from "../../components/Refrigerator/LeftBottomTwoWidgets/LeftBottomTwoWidgets";
import RefrigeratorHistory from "../../components/Refrigerator/RefrigeratorHistory/RefrigeratorHistory";

const Refrigerator = () => {
  const { pollingInterval, setSideBarShow } = useContext(AppContext);
  const [refetch, setRefetch] = useState(true);
  const { data, refreshDataImmediate } = useFetch(
    API_ENDPOINT.REFRIDGERATOR,
    LOCAL_ENDPOINT.REFRIDGERATOR,
    refetch,
    pollingInterval,
  );

  // const data = refData;

  const [settingPopup, setSettingPopup] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    if (data?.hideSidebar) {
      setSideBarShow(data?.hideSidebar);
    }
  }, [data]);

  const toggleSettingPopup = () => {
    setSettingPopup((prev) => !prev);
  };

  return (
    <DataContext.Provider
      value={{
        refreshParentData: "refreshDataImmediate",
      }}
    >
      <div className={styles.mainContainer}>
        {/* left div */}
        <div className={styles.leftDiv}>
          <div>
            <div className={styles.leftDivTop}>
              <div className={styles.backNav} onClick={() => navigate(-1)}>
                <div className={styles.backContainer}>
                  <BackIcon />
                </div>
                <p className={styles.backText}>Back</p>
              </div>
              <div className={styles.settingsContainer} onClick={toggleSettingPopup}>
                <SettingsIcon />
              </div>
            </div>
            <h2 className={styles.lightingHeadingText}>
              {data?.overview?.title?.split(" ")?.map((word, ind) => (
                <p className="m-0" key={ind}>
                  {word}
                </p>
              )) || REFRIDGERATOR_TITLE}
            </h2>
          </div>
          <LeftBottomTwoWidgets data={data} />
        </div>
        {/* right div */}
        <div className={styles.mainRight}>
          <div className={styles.rightDiv}>
            <div className={styles.rightTop}>
              <FridgeIcon />
              <div className={styles.centerTextDiv}>
                <h2 className={styles.lightMasterText}>{data?.controls?.history?.title || "Temperature History"}</h2>
                {/* <p className={styles.lightsOnText}>
                  {data?.controls?.history?.subtext || "Alert On"}
                </p> */}
              </div>
            </div>
            <div className={styles.rightBottomDiv}>
              <RefrigeratorHistory data={data} />
            </div>
          </div>
        </div>
      </div>

      {settingPopup && (
        <Popup width="50%" top="50px" closePopup={toggleSettingPopup}>
          <RefrigeratorSettings togglePopup={toggleSettingPopup} parentRefetch={setRefetch} />
        </Popup>
      )}
    </DataContext.Provider>
  );
};

export default Refrigerator;
