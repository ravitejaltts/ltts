import React, { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../../context/AppContext";
import { BackIcon, Pet } from "../../assets/asset";
import Switch from "../../components/common/switch/Switch";
import { DataContext } from "../../context/DataContext";
import { useFetch } from "../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../utils/api";
import styles from "./pet.module.css";
import TempBox from "../../components/pet-monitoring/temp-box/TempBox";

const PetMonitoring = () => {
  const navigate = useNavigate();
  const { pollingInterval, setSideBarShow } = useContext(AppContext);
  const { data, refreshDataImmediate } = useFetch(
    API_ENDPOINT.PET_MONITORING,
    LOCAL_ENDPOINT.PET_MONITORING,
    true,
    pollingInterval,
  );

  //   useEffect(() => {
  //     if (data) {
  //       setDataToLocal("climate-bottom-widget-data", data.overview);
  //       setDataToLocal("climate-therostat-data", data.climateZones[0].thermostat);
  //       setDataToLocal("climate-roof-fans-data", data.roofFans);
  //       setBottomWidgetData(data.overview);
  //       setThermostatData(data.climateZones[0].thermostat);
  //       setRoofFans(data.roofFans);

  //       if (data?.hideSidebar) {
  //         setSideBarShow(data?.hideSidebar);
  //       }
  //     }
  //   }, [data]);

  const tempBoxActive = !!data?.features?.[0]?.state?.onOff;

  const renderSupportText = (data) => {
    return <p className={styles.text}>{data?.text}</p>;
  };

  const renderPetBox = (data) => {
    return (
      <>
        <div className={styles.rightDiv}>
          {!tempBoxActive && <div className={styles.disable}></div>}
          <div className={styles.rowLayout}>
            <Pet className={`${!tempBoxActive && styles.disableIcon}`} />
            <div className={styles.centerTextDiv}>
              <p className={`${styles.lightMasterText} ${!tempBoxActive && styles.disableText1}`}>{data?.title}</p>
              <p className={`${styles.lightsOnText} ${!tempBoxActive && styles.disableText1}`}>{data?.subtext}</p>
            </div>
            <div className={styles.onTop}>
              <Switch
                onOff={data.state?.onOff}
                action={data.actions?.TAP?.action}
                refreshParentData={refreshDataImmediate}
              />
            </div>
          </div>
        </div>

        <TempBox data={data?.petMonitoring} enable={data.state?.onOff} refeshParentData={refreshDataImmediate} />
      </>
    );
  };

  return (
    <DataContext.Provider value={{ refreshParentData: refreshDataImmediate }}>
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
              {/* <div
                className={styles.settingsContainer}
                onClick={openSettingModal}
              >
                <SettingsIcon />
              </div> */}
            </div>
            <h2 className={styles.lightingHeadingText}>
              {data?.overview?.title?.split(" ")?.map((word, ind) => (
                <p className="m-0" key={ind}>
                  {word}
                </p>
              ))}
            </h2>
            <h4 className={styles.outdoorTemp}>{data?.overview?.subtext}</h4>
          </div>

          <div className={styles.leftBottomContainer}>
            <div className={styles.leftBottomDiv}>
              <h1
                className={styles.fText}
                style={{
                  fontWeight: data?.overview?.bottom_widget?.text === "--" ? "normal" : "bold",
                }}
              >
                {data?.overview?.bottom_widget?.text || 72}
                <span className={styles.fSmallText}>{data?.overview?.bottom_widget?.sidetext}</span>
              </h1>
              <p className={styles.currentText}>{data?.overview?.bottom_widget?.subtext}</p>
            </div>
          </div>
        </div>
        {/* right div */}
        <div className={styles.mainRight}>
          {data?.features?.map((tempData, i) => (
            <React.Fragment key={i}>
              {tempData?.type === "Simple" && renderPetBox(tempData)}
              {tempData?.type === "SUPPORT_TEXT" && renderSupportText(tempData)}
            </React.Fragment>
          ))}
        </div>
      </div>
    </DataContext.Provider>
  );
};

export default PetMonitoring;
