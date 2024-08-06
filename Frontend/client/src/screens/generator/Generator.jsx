import { useContext, useState } from "react";
import { AppContext } from "../../context/AppContext";
import { RoundAlert } from "../../assets/asset";
import { GeneratorIcon, GeneratorPowerIcon, QuietHoursIcon } from "../../assets/assets";
import Popup from "../../components/common/Popup/Popup";
import GeneratorSettings from "./generator-settings/GeneratorSettings";
import { useFetch } from "../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../utils/api";
import Switch from "../../components/common/switch/Switch";
import Row from "../../components/water-system/row/Row";
import GeneratorHeading from "./GeneratorHeading";
import GeneratorHeadingBottom from "./GeneratorHeadingBottom";
import styles from "./generator.module.css";
import GeneratorBodyHeading from "./GeneratorBodyHeading";
import GeneratorStop from "./GeneratorStop";

const iconObj = {
  default: <GeneratorIcon />,
  GeneratorQuietHours: <QuietHoursIcon />,
};

function Generator() {
  const { pollingInterval } = useContext(AppContext);
  const { data, refreshDataImmediate } = useFetch(
    API_ENDPOINT.GENERATOR_SCREEN,
    LOCAL_ENDPOINT.GENERATOR_SCREEN,
    true,
    pollingInterval,
  );
  const [showModal, setShowModal] = useState(false);
  const generatorsArray = data?.generators || [];
  const mainGenerator = generatorsArray[0];

  const openSettingModal = () => {
    setShowModal(true);
  };

  const closeSettingModal = () => {
    setShowModal(false);
  };

  if (!generatorsArray || !mainGenerator) {
    return null;
  }

  const lockoutsArray = generatorsArray[0]?.lockouts;
  const switchesData = generatorsArray[0]?.switches;
  const stopButtonData = switchesData[0];
  const featureSwitches = data?.switches ?? [];

  // const refreshWrapperValue = useMemo(() => ({ refreshParentData: refreshDataImmediate }), [refreshDataImmediate]);
  return (
    // <DataContext.Provider value={refreshWrapperValue}>
    <>
      <div generator="" className="mainContainer">
        <div className="screenHeader">
          <GeneratorHeading data={data} settings={openSettingModal} />
          <GeneratorHeadingBottom data={data} />
        </div>

        <div className="screenBody">
          <div className="screenCard">
            {!!lockoutsArray?.length && (
              <div className="card p-3 d-flex align-center" style={{borderBottomRightRadius: 0, borderBottomLeftRadius: 0 }}>
                <RoundAlert className={styles.roundAlert} />
                <div className={styles.centerTextDiv}>
                  <h2 className={`${styles.lightMasterText} `}>{lockoutsArray[0]?.title}</h2>
                  <p
                    className={`${styles.lightsOnText} `}
                    dangerouslySetInnerHTML={{
                      __html: lockoutsArray[0]?.subtext?.replace(
                        "{timer}",
                        `<span class="dangerour">${lockoutsArray[0]?.state?.timer}</span>`,
                      ),
                    }}
                  >
                    {/* {lockoutsArray[0]?.subtext?.replace(
                      "{timer}",
                      lockoutsArray[0]?.state?.timer
                    )} */}
                  </p>
                </div>
              </div>
            )}
            {/* Set a gap conditional to lockouts being present */}
            {generatorsArray[0]?.lockouts?.length > 0 && <div className={styles.gap} />}

            <GeneratorBodyHeading generatorsArray={generatorsArray} />
            <div className="screenCardBody align-center">
              <GeneratorStop stopButtonData={stopButtonData} generator={mainGenerator} />

              {/* Future layout
               <div className="d-flex">
                <div className="col w-50 p-1 pe-3">
                  <div className="card p-3">
                    <GeneratorStop stopButtonData={stopButtonData} generator={mainGenerator} />
                  </div>
                </div>
                <div className="col w-25 p-1">
                  <div className="card p-3">Power</div>
                  <div className="card p-3 mt-2">Current</div>
                </div>
                <div className="col p-1">
                  <div className="card p-3">Voltage</div>
                  <div className="card p-3 mt-2">Frequency</div>
                </div>
              </div> */}

              {!!switchesData?.[1] && (
                <div>
                  <GeneratorPowerIcon />
                  <div className={styles.centerTextDiv}>
                    <p>{switchesData?.[1]?.title}</p>
                    <p>{switchesData?.[1]?.subtext}</p>
                  </div>
                  <div>
                    <Switch
                      onOff={switchesData?.[1]?.state.onOff}
                      action={switchesData?.[1]?.actions?.PRESS.action}
                      refreshParentData={refreshDataImmediate}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
          {/* Iterate over other generator features */}
          {featureSwitches.map((row) => (
            <Row
              key={row.name}
              icon={iconObj[row.name] || iconObj.default}
              title={row.title}
              subtext={row.subtext}
              onOff={row?.state?.quietTimeOnOff}
              action={row.actions?.PRESS.action}
              params={{ quietTimeOnOff: row?.state?.quietTimeOnOff ? 0 : 1 }}
              type={row?.type}
            />
          ))}
        </div>
      </div>
      {showModal && (
        <Popup width="50%" top="50px" closePopup={closeSettingModal}>
          <GeneratorSettings />
        </Popup>
      )}
    </>
    // </DataContext.Provider>
  );
}

export default Generator;
