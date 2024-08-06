import { useContext, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../../context/AppContext";
import { BackIcon, EnergyIcon, HouseBatteryLevel, SettingsIcon, WaterHeater } from "../../assets/asset";
import { ACPower, CookTop, Heater, Microwave } from "../../assets/inverterIcons";
import DetailRow from "../../components/common/detail-row/DetailRow";
import Popup from "../../components/common/Popup/Popup";
import Switch from "../../components/common/switch/Switch";
import LevelWidget from "../../components/home/levelwidget/LevelWidget";
import InverterSettings from "../../components/inverter/inverter-setting/InverterSettings";
import { DataContext } from "../../context/DataContext";
import { useFetch } from "../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../utils/api";
import styles from "./inverter.module.css";

const iconsObj = {
  "Water Heater": <WaterHeater />,
  Heater: <Heater />,
  "AC Power Outlets": <ACPower />,
  "Cook Top": <CookTop />,
  Microwave: <Microwave />,
};

function Inverter() {
  const navigate = useNavigate();
  const { pollingInterval, setSideBarShow } = useContext(AppContext);
  const { data, refreshDataImmediate } = useFetch(
    API_ENDPOINT.INVERTER,
    LOCAL_ENDPOINT.INVERTER,
    true,
    pollingInterval,
  );
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    if (data?.hideSidebar) {
      setSideBarShow(data?.hideSidebar);
    }
  }, [data]);

  const toggleSettingModal = () => {
    setShowModal((prev) => !prev);
  };

  const refreshWrapperValue = useMemo(() => ({ refreshParentData: refreshDataImmediate }), [refreshDataImmediate]);
  return (
    <DataContext.Provider value={refreshWrapperValue}>
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
              <div className={styles.settingsContainer} onClick={toggleSettingModal}>
                <SettingsIcon />
              </div>
            </div>
            <h2 className={styles.lightingHeadingText}>{data?.overview?.title}</h2>
          </div>

          <div className={styles.leftBottomContainer}>
            <LevelWidget
              height="218px"
              width="109px"
              key="1"
              icon={<HouseBatteryLevel />}
              data={data && data?.levels[0]}
              cls="inverter-icon"
            />
          </div>
        </div>
        {/* right div */}
        <div className={styles.mainRight}>
          <div className={styles.rightDiv}>
            <div className={styles.rightTop}>
              <div className={styles.energyIconSmall}>
                <EnergyIcon />
              </div>
              <div className={styles.centerTextDiv}>
                <h2 className={styles.lightMasterText}>{data?.main?.title}</h2>
                <p className={styles.lightsOnText}>{data?.main?.subtext}</p>
              </div>

              <Switch
                onOff={data?.main?.Simple?.onOff}
                action={data?.main?.action_default?.action}
                refreshParentData={refreshDataImmediate}
              />
            </div>
            <div className={styles.rightBottomDiv}>
              <div className={styles.menuHeading}>{data?.navList?.title}</div>
              <div className={styles.infoContainer}>
                {data?.navList?.data?.map((item, i) => (
                  <div key={i}>
                    <DetailRow
                      icon={iconsObj[item?.title]}
                      name={item?.title}
                      arrow={item?.action_default}
                      actionHref={item?.action_default?.action?.href}
                      noBorder={i + 1 === data?.navList?.data?.length}
                    />
                  </div>
                ))}
                {/* <div>
                    <DetailRow
                      icon={<WaterHeater />}
                      name="Water Heater"
                      arrow
                    />
                  </div>
                  <div>
                    <DetailRow icon={<Heater />} name="Heater" arrow />
                  </div>
                  <div>
                    <DetailRow
                      icon={<ACPower />}
                      name="AC Power Outlets"
                      arrow
                    />
                  </div>
                  <div>
                    <DetailRow icon={<CookTop />} name="Cook Top" arrow />
                  </div>
                  <div>
                    <DetailRow icon={<Microwave />} name="Microwave" arrow />
                  </div> */}
              </div>
            </div>
          </div>
        </div>
      </div>

      {showModal && (
        <Popup width="50%" top="50px" closePopup={toggleSettingModal}>
          <InverterSettings />
        </Popup>
      )}
    </DataContext.Provider>
  );
}

export default Inverter;
