import axios from "axios";
import { useContext, useEffect, useMemo, useState } from "react";
import { useFetch } from "../../hooks/useFetch";
import { AppContext } from "../../context/AppContext";
import { InfoIconBlue, RoundAlert, WaterHeaterIcon, WaterPumpIcon, WavesIcon } from "../../assets/asset";
import Popup from "../../components/common/Popup/Popup";
import Row from "../../components/water-system/row/Row";
import { DataContext } from "../../context/DataContext";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../utils/api";
import styles from "./water.module.css";
import screenStyles from "../../style/screen.css";
import WaterHeaterWarningModal from "../../components/water-system/WaterHeaterWarningModal/WaterHeaterWarningModal";
import WaterHeading from "./WaterHeading";
import WaterHeadingBottom from "./WaterHeadingBottom";
import WaterSettings from "../../components/water-system/water-settings/WaterSettings";

const iconObj = {
  FreshWaterPumpToggle: <WaterPumpIcon />,
  WaterHeaterToggle: <WaterHeaterIcon />,
  TankPadToggle: <WavesIcon />,
};

function WaterSystem() {
  const { pollingInterval, setSideBarShow } = useContext(AppContext);
  const { data, refreshDataImmediate } = useFetch(
    API_ENDPOINT.WATER_SYSTEM,
    LOCAL_ENDPOINT.WATER_SYSTEM,
    true,
    pollingInterval,
  );
  // const navigate = useNavigate();
  const [showModal, setShowModal] = useState(false);
  const [selected, setSelected] = useState("Comfort");
  const [showInfo, setShowInfo] = useState(false);
  const waterHeaterData = data?.switches[0];
  const lockoutData = data?.switches[0]?.lockouts;

  useEffect(() => {
    if (data?.hideSidebar) {
      setSideBarShow(data?.hideSidebar);
    }
    if (data) {
      const withTrueOptions = waterHeaterData?.extras?.mode?.options?.filter((opt) => opt?.selected === true);
      if (withTrueOptions?.length === 1) {
        setSelected(withTrueOptions[0]?.value);
      } else {
        setSelected(waterHeaterData?.extras?.mode?.options[0]?.value);
      }
    }
  }, [data]);

  /*  const openSettingModal = () => {
      navigate(data?.overview.settings.href);
  }; */

  const openSettingModal = () => {
    setShowModal(true);
  };

  const closeSettingModal = () => {
    setShowModal(false);
  };

  const toggleInfoModal = () => {
    setShowInfo(!showInfo);
  };

  const handleModeChange = (val) => {
    setSelected(val);
    axios
      .put(waterHeaterData?.action_default?.action?.href, { mode: val })
      .then(() => {})
      .catch((err) => console.error(err));
  };

  const refreshWrapperValue = useMemo(() => ({ refreshParentData: refreshDataImmediate }), [refreshDataImmediate]);

  return (
    <DataContext.Provider value={refreshWrapperValue}>
      <div watersystems="" className="mainContainer">
        <div className="screenHeader">
          <WaterHeading title={data?.overview?.title} settings={openSettingModal} />
          <WaterHeadingBottom levels={data?.levels} />
        </div>

        <div className="screenBody">
          {/* <div className={styles.lockoutCont}>
            {lockoutData?.map((lockout, ind) => (
              <div className={`${styles.rightTop} `} key={ind}>
                <RoundAlert className={styles.roundAlert} />
                <div className={styles.centerTextDiv}>
                  <h2 className={`${styles.lightMasterText} `}>
                    {lockout?.title}
                  </h2>
                  <p
                    className={`${styles.lightsOnText} `}
                    // dangerouslySetInnerHTML={{
                    //   __html: lockout?.subtext?.replace(
                    //     "{timer}",
                    //     `<span className="dangerour">${lockout?.state?.timer}</span>`
                    //   ),
                    // }}
                  >
                    {lockout?.subtext}
                  </p>
                </div>
              </div>
            ))}
          </div> */}
          <div className="screenCard">
            {lockoutData?.map((lockout, ind) => (
              <div className={`${screenStyles.screenCardHeader} `} key={ind}>
                <RoundAlert />
                <div className={styles.centerTextDiv}>
                  <h2 className={`${styles.lightMasterText} `}>{lockout?.title}</h2>
                  <p
                    className={`${styles.lightsOnText} `}
                    // dangerouslySetInnerHTML={{
                    //   __html: lockout?.subtext?.replace(
                    //     "{timer}",
                    //     `<span className="dangerour">${lockout?.state?.timer}</span>`
                    //   ),
                    // }}
                  >
                    {lockout?.subtext}
                  </p>
                </div>
              </div>
            ))}
            <Row
              key={waterHeaterData?.name}
              icon={iconObj[waterHeaterData?.name] || iconObj.FreshWaterPumpToggle}
              title={waterHeaterData?.title}
              subtext={waterHeaterData?.subtext}
              onOff={waterHeaterData?.state?.onOff}
              action={waterHeaterData?.action_default.action}
              stylesExtra={{ marginBottom: 0, borderRadius: 0 }}
              params={{ onOff: waterHeaterData?.state?.onOff ? 0 : 1 }}
              disabled={!!lockoutData?.length}
            />
            <div className={`${styles.heaterExtras} ${lockoutData?.length ? styles.disabled : ""}`}>
              <div className={styles.modeControls}>
                <div className={styles.modeLeft}>
                  <p className={styles.modeText}>{waterHeaterData?.extras?.mode?.text}</p>
                  <InfoIconBlue onClick={lockoutData?.length ? () => {} : toggleInfoModal} />
                </div>
                <div className={styles.modeRightTabs}>
                  {waterHeaterData?.extras?.mode?.options?.map((option) => (
                    <div
                      key={option?.value}
                      className={`${styles.pillToggleButton} ${
                        selected === option?.value ? styles.pillToggleButtonActive : ""
                      }`}
                      onClick={
                        lockoutData?.length ? () => {} : () => handleModeChange(option?.value)
                        // : () => setSelected(option?.value)
                      }
                    >
                      {option?.key}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
          {data?.switches?.slice(1, data?.switches?.length)?.map((row) => (
            <Row
              key={row.name}
              icon={iconObj[row.name] || iconObj.FreshWaterPumpToggle}
              title={row.title}
              subtext={row.subtext}
              onOff={row?.state?.onOff}
              action={row.action_default.action}
              params={{ onOff: row?.state?.onOff ? 0 : 1 }}
              type={row?.type}
            />
          ))}
        </div>
      </div>
      {showModal && (
        <Popup width="50%" top="50px" closePopup={closeSettingModal}>
          <WaterSettings handleClose={closeSettingModal} />
        </Popup>
      )}
      {showInfo && (
        <Popup width="60%" top="30%" closePopup={toggleInfoModal}>
          <WaterHeaterWarningModal
            toggleInfoModal={toggleInfoModal}
            information={waterHeaterData?.extras?.mode?.information}
          />
        </Popup>
      )}
    </DataContext.Provider>
  );
}

export default WaterSystem;
