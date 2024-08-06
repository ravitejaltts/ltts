import axios from "axios";
import { useContext, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../../context/AppContext";
import {
  ActiveCool,
  ActiveHeat,
  BackIcon,
  InactiveCool,
  InactiveHeat,
  MinusIcon,
  PlusIcon,
  RoofVent,
  SettingsIcon,
  ThermostatIcon,
} from "../../assets/asset";
import Popup from "../../components/common/Popup/Popup";
import Switch from "../../components/common/switch/Switch";
import { getDataFromLocal, setDataToLocal } from "../../components/constants/helper";
import { DataContext } from "../../context/DataContext";
import { useFetch } from "../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../utils/api";
import ClimateSettings from "../climate-settings/ClimateSettings";
import { EVENTVALUES } from "../../constants/CONST";
import HeatSourceAndFan from "../../components/climate-control/heatSourceAndAcFan/HeatSourceAndFan";
import HeatSourceModal from "../../components/climate-control/heatSourceAndAcFan/HeatSourceModal";
import FanModal from "../../components/climate-control/heatSourceAndAcFan/FanModal";
import styles from "./climate.module.css";

function ClimateControl() {
  const navigate = useNavigate();
  const { pollingInterval, setSideBarShow } = useContext(AppContext);
  const { data, refreshDataImmediate } = useFetch(
    API_ENDPOINT.CLIMATE_CONTROL,
    LOCAL_ENDPOINT.CLIMATE_CONTROL,
    true,
    pollingInterval,
  );
  const [activeBtn, setActiveBtn] = useState();
  const [tempMode, setTempMode] = useState(EVENTVALUES.AUTO);
  const [showModal, setShowModal] = useState(null);

  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [bottomWidgetData, setBottomWidgetData] = useState(getDataFromLocal("climate-bottom-widget-data"));
  const [thermostatData, setThermostatData] = useState(getDataFromLocal("climate-therostat-data"));
  const [roofFans, setRoofFans] = useState(getDataFromLocal("climate-roof-fans-data"));

  useEffect(() => {
    if (data) {
      setDataToLocal("climate-bottom-widget-data", data.overview);
      setDataToLocal("climate-therostat-data", data.climateZones[0].thermostat);
      setDataToLocal("climate-roof-fans-data", data.roofFans);
      setBottomWidgetData(data.overview);
      setThermostatData(data.climateZones[0].thermostat);
      setRoofFans(data.roofFans);
      const selected = data?.climateZones[0].thermostat?.climateMode?.ToggleButton?.options.find(
        (item) => item?.selected ?? false,
      );
      if (selected !== undefined) {
        // console.log("Climate mode: " + JSON.stringify(selected));
        setActiveBtn(selected.value);
      }
      if (data?.hideSidebar) {
        setSideBarShow(data?.hideSidebar);
      }
    }
  }, [data]);

  const openSettingModal = () => {
    setShowSettingsModal(true);
  };

  const closeSettingModal = () => {
    setShowSettingsModal(false);
  };

  const changeTempMode = (value) => {
    if (activeBtn === EVENTVALUES.AUTO) {
      setTempMode(value);
    }
  };

  // api calling put
  const changeThermoMode = (value) => {
    axios
      .put(thermostatData?.climateMode?.ToggleButton?.action_default?.action?.href, {
        item: "ClimateMode",
        value,
      })
      .then(() => {
        // let newData = value === 519 ? "AUTO" : value === 518 ? "HEAT" : "COOL";
        setActiveBtn(value);
        refreshDataImmediate();
      });
  };

  // const changeAcFanSpeed = (value) => {
  //   axios.put(thermostatData?.acFanSpeed?.ToggleButton?.action_default?.action.href, { fanMode: value }).then((res) => {
  //     refreshDataImmediate();
  //   });
  // };

  const changeRoofFan = (type, value, roofFan) => {
    const speed = roofFan?.AdvancedFan?.fanSpd?.options.find((item) => item.selected === true);
    const direction = roofFan?.AdvancedFan?.direction?.options.find((item) => item.selected === true);
    const dome = roofFan?.AdvancedFan?.dome?.options.find((item) => item.selected === true);

    const obj = {
      direction: direction?.value,
      dome: dome?.value,
      fanSpd: speed?.value,
    };

    obj[type] = value;

    axios.put(roofFan?.action_default?.action?.href, obj).then(() => {
      refreshDataImmediate();
    });
  };

  const changeTempApiCall = (type, value) => {
    // TODO: Use the numerical modes in the backend
    const mode =
      // eslint-disable-next-line no-nested-ternary
      activeBtn === EVENTVALUES.AUTO
        ? tempMode === EVENTVALUES.HEAT
          ? "HEAT"
          : "COOL"
        : activeBtn === EVENTVALUES.HEAT
          ? "HEAT"
          : "COOL";
    if (type === "increase") {
      axios
        .put(thermostatData?.tempBand?.increase_temp?.action?.href, {
          mode,
          setTemp: value,
        })
        .then(() => {
          refreshDataImmediate();
        });
    } else {
      axios
        .put(thermostatData?.tempBand?.decrease_temp?.action?.href, {
          mode,
          setTemp: value,
        })
        .then(() => {
          refreshDataImmediate();
        });
    }
  };

  // const changeFanDirection = (value, roofFan) => {
  //   changeRoofFan("direction", value, roofFan);
  // };

  const changeFanSpeed = (value, roofFan) => {
    changeRoofFan("fanSpd", value, roofFan);
  };

  // const changeFanMode = (value) => {
  //   changeRoofFan("onOff", value);
  // };

  const changeRoofHatch = (value, roofFan) => {
    changeRoofFan("dome", value, roofFan);
  };

  const changeTemp = (value) => {
    if (activeBtn === EVENTVALUES.HEAT || (activeBtn === EVENTVALUES.AUTO && tempMode === EVENTVALUES.HEAT)) {
      const newValue = (thermostatData?.tempBand?.setTempHeat || 0) + value;
      // if (newValue < thermostatData?.tempBand?.setTempCool) {
      if (value > 0) {
        changeTempApiCall("increase", newValue);
      } else {
        changeTempApiCall("decrease", newValue);
      }

      // }
    } else {
      const newValue = (thermostatData?.tempBand?.setTempCool || 0) + value;
      // if (newValue > thermostatData?.tempBand?.setTempHeat) {
      if (value > 0) {
        changeTempApiCall("increase", newValue);
      } else {
        changeTempApiCall("decrease", newValue);
      }
      // }
    }
  };

  const tempBoxActive = useMemo(() => !!thermostatData?.master?.Simple?.onOff, [thermostatData?.master?.Simple?.onOff]);

  const changeModal = (modal) => {
    if (!tempBoxActive) {
      setShowModal(null);
      return;
    }
    setShowModal(modal);
  };

  const closeModal = (modal) => {
    setShowModal(modal);
  };

  const getClimateModeClass = (item) => {
    return `${item.selected && thermostatData?.master?.Simple?.onOff && styles.pillToggleButtonActive} ${
      // eslint-disable-next-line no-nested-ternary
      item.value === EVENTVALUES.AUTO
        ? styles.leftBtn
        : item.value === EVENTVALUES.HEAT || item.value === EVENTVALUES.COOL
          ? styles.heatBtn
          : styles.rightBtn
    }
                        ${!tempBoxActive && styles.disableText2}`;
  };

  const refreshWrapperValue = useMemo(() => ({ refreshParentData: refreshDataImmediate }), [refreshDataImmediate]);

  return (
    <DataContext.Provider value={refreshWrapperValue}>
      {showModal === "heat-modal" && (
        <HeatSourceModal
          changeModal={closeModal}
          heatData={thermostatData?.heatSource}
          refreshDataImmediate={refreshDataImmediate}
        />
      )}
      {showModal === "fan-modal" && (
        <FanModal
          changeModal={closeModal}
          fanData={thermostatData?.acFanSpeed}
          refreshDataImmediate={refreshDataImmediate}
        />
      )}
      <div climatecontrol="" className="mainContainer">
        {/* left div */}
        <div className="screenHeader">
          <div>
            <div className="headerTopControls">
              <div className="backNav" onClick={() => navigate(-1)}>
                <div className="backContainer">
                  <BackIcon />
                </div>
                <p className="backText">Back</p>
              </div>
              <div className={styles.settingsContainer} onClick={openSettingModal}>
                <SettingsIcon />
              </div>
            </div>
            <h2 className={styles.lightingHeadingText}>
              {bottomWidgetData?.title?.split(" ")?.map((word, ind) => (
                <p className="m-0" key={ind}>
                  {word}
                </p>
              ))}
            </h2>
            <h4 className={styles.outdoorTemp}>{bottomWidgetData?.subtext}</h4>
          </div>

          <div className={styles.leftBottomContainer}>
            <div className={styles.leftBottomDiv}>
              <h1
                className={styles.fText}
                style={{
                  fontWeight: bottomWidgetData?.bottom_widget?.text === "--" ? "normal" : "bold",
                }}
              >
                {bottomWidgetData?.bottom_widget?.text}
                <span className={styles.fSmallText}>{bottomWidgetData?.bottom_widget?.sidetext}</span>
              </h1>
              <p className={styles.currentText}>{bottomWidgetData?.bottom_widget?.subtext}</p>
            </div>
          </div>
        </div>

        {/* right div */}
        <div className="screenBody">
          <div className="screenCard">
            {!tempBoxActive && <div className={styles.disable}></div>}
            <div className={styles.rowLayout} style={{ marginBottom: 0, borderRadius: 0 }}>
              <ThermostatIcon className={`${!tempBoxActive && styles.disableIcon}`} />
              <div className={styles.centerTextDiv}>
                <p className={`${styles.lightMasterText} ${!tempBoxActive && styles.disableText1}`}>
                  {thermostatData?.master?.title}
                </p>
                <p className={`${styles.lightsOnText} ${!tempBoxActive && styles.disableText1}`}>
                  {thermostatData?.master?.subtext}
                </p>
              </div>
              <div className={styles.onTop}>
                <Switch
                  onOff={thermostatData?.master?.Simple?.onOff}
                  action={thermostatData?.master?.action_default?.action}
                  refreshParentData={refreshDataImmediate}
                />
              </div>
            </div>
            <div className={styles.rightBottomDiv}>
              <div className={styles.btnContainer}>
                {thermostatData?.climateMode?.ToggleButton?.options.map((item, ind) => (
                  <div key={ind} className={getClimateModeClass(item)} onClick={() => changeThermoMode(item.value)}>
                    {item.key}
                  </div>
                ))}
              </div>
              {activeBtn !== EVENTVALUES.FAN_ONLY && (
                <div className={styles.thermoContent}>
                  {/* eslint-disable-next-line jsx-a11y/control-has-associated-label */}
                  <button
                    type="button"
                    className={`${styles.minusContainer} ${
                      (activeBtn === EVENTVALUES.AUTO && tempMode === EVENTVALUES.HEAT) ||
                      activeBtn === EVENTVALUES.HEAT
                        ? styles.orangeText
                        : styles.blueText
                    } ${!tempBoxActive && styles.disableText2}`}
                    onClick={() => {
                      changeTemp(-1);
                    }}
                  >
                    <MinusIcon />
                  </button>
                  {!tempBoxActive && (
                    <div className={`${styles.heatContainer} `}>
                      <div style={{ gap: "6px", padding: "0 10px" }} className="flex justify-center align-center">
                        <h1 className={`${styles.tempText} ${styles.disableText2}`}>Off</h1>
                      </div>
                    </div>
                  )}

                  {activeBtn !== EVENTVALUES.COOL && tempBoxActive && (
                    <div
                      className={`${styles.heatContainer} ${
                        activeBtn === EVENTVALUES.HEAT ||
                        (activeBtn === EVENTVALUES.AUTO && tempMode === EVENTVALUES.HEAT)
                          ? styles.orangeBorder
                          : styles.transBoarder
                        // && styles.orangeBorder
                      } ${activeBtn === EVENTVALUES.COOL && styles.offText}`}
                      onClick={() => changeTempMode(EVENTVALUES.HEAT)}
                    >
                      {activeBtn === EVENTVALUES.HEAT || activeBtn === EVENTVALUES.AUTO ? (
                        <div style={{ gap: "6px", padding: "0 10px" }} className="flex justify-center align-center">
                          <ActiveHeat />{" "}
                          <h1 className={styles.tempText}>
                            {thermostatData?.tempBand?.setTempHeat}
                            <span className={styles.fSmallText}>{thermostatData?.tempBand?.setTempHeatText}</span>
                          </h1>
                        </div>
                      ) : (
                        <>
                          <InactiveHeat /> Off
                        </>
                      )}
                    </div>
                  )}
                  {activeBtn !== EVENTVALUES.HEAT && tempBoxActive && (
                    <div
                      className={`${styles.coolContainer} ${
                        activeBtn === EVENTVALUES.COOL ||
                        (activeBtn === EVENTVALUES.AUTO && tempMode === EVENTVALUES.COOL)
                          ? styles.blueBorder
                          : styles.transBorder
                        // styles.blueBorder
                        // styles.transBorder
                      } ${activeBtn === EVENTVALUES.HEAT && styles.offText}`}
                      onClick={() => {
                        changeTempMode(EVENTVALUES.COOL);
                        console.log(activeBtn);
                      }}
                    >
                      {activeBtn === EVENTVALUES.COOL || activeBtn === EVENTVALUES.AUTO ? (
                        <>
                          <ActiveCool />
                          <h1 className={styles.tempText}>
                            {thermostatData?.tempBand?.setTempCool}
                            <span className={styles.fSmallText}>{thermostatData?.tempBand?.setTempCoolText}</span>
                          </h1>
                        </>
                      ) : (
                        <>
                          <InactiveCool /> Off
                        </>
                      )}
                    </div>
                  )}
                  {/* eslint-disable-next-line jsx-a11y/control-has-associated-label */}
                  <button
                    type="button"
                    className={`${styles.plusContainer} ${
                      (activeBtn === EVENTVALUES.AUTO && tempMode === EVENTVALUES.HEAT) ||
                      activeBtn === EVENTVALUES.HEAT
                        ? styles.orangeText
                        : styles.blueText
                    } ${!tempBoxActive && styles.disableText2}`}
                    onClick={() => {
                      changeTemp(+1);
                    }}
                  >
                    <PlusIcon />
                  </button>
                </div>
              )}
              <HeatSourceAndFan
                changeModal={changeModal}
                closeModal={closeModal}
                tempBoxActive={tempBoxActive}
                thermostatData={thermostatData}
              />
              {/* {thermostatData?.acFanSpeed?.ToggleModal?.options.length > 1 && (
                <div className={`${styles.hatchOption}`}>
                  <p className={` ${!tempBoxActive && styles.disableText2} `}>
                    {thermostatData?.acFanSpeed?.text}
                  </p>
                  <div
                    className={`${styles.btnContainer} ${styles.fanContainer}`}
                  >
                    {thermostatData?.acFanSpeed?.ToggleModal?.options.map(
                      (item) => (
                        <div
                          className={`${styles.selectOptions} ${
                            item.selected &&
                            thermostatData?.master?.Simple?.onOff &&
                            styles.activeBtn
                          } ${!tempBoxActive && styles.disableText2}`}
                          key={item?.value}
                          value={item?.value}
                          selected={item.selected}
                          onClick={() => changeAcFanSpeed(item.value)}
                        >
                          {item?.key}
                        </div>
                      )
                    )}
                  </div>
                </div>
              )} */}
            </div>
          </div>

          {/* Iterate over the Roof Fans */}
          {roofFans?.map((roofFan) => {
            // Set this to perma enabled due to being stateless
            // const roofHatchBoxActive = roofFan?.AdvancedFan?.dome;
            const roofHatchBoxActive = true;
            return (
              <div className={styles.roofHatch} key={roofFan.title}>
                {!roofHatchBoxActive && <div className={styles.disable}></div>}
                <div className={styles.rowLayout}>
                  <RoofVent className={`${!roofHatchBoxActive && styles.disableIcon}`} />
                  <div className={styles.noDividercenterTextDiv}>
                    <p className={`${styles.lightMasterText} ${!roofHatchBoxActive && styles.disableText1}`}>
                      {roofFan?.title}
                    </p>
                    <p className={`${styles.lightsOnText} ${!roofHatchBoxActive && styles.disableText1}`}>
                      {roofFan?.subtext}
                    </p>
                  </div>
                  {/* <div className={styles.onTop}>
                    <Switch2
                      onOff={roofFan?.AdvancedFan?.dome}
                      action={changeRoofHatch}
                      roofFan={roofFan}
                    />
                  </div> */}
                </div>
                <div className={styles.roofHatchContent}>
                  <div
                    className={`${styles.hatchOption} ${styles.fanOption} ${
                      !roofHatchBoxActive && styles.disableText2
                    }`}
                  >
                    <p className={styles.fanText}>{roofFan?.AdvancedFan?.dome?.title}</p>
                    {/* Old Stateful buttons */}
                    {/* <div className={styles.selectStatelessContainerFan}>
                      {roofFan?.AdvancedFan?.dome?.options?.map((item, ind) => (
                        <div
                          className={`${styles.selectOptions} ${
                            item.selected &&
                            roofFan?.AdvancedFan?.dome &&
                            styles.activeBtn
                          }
                        ${
                          ind !==
                            roofFan?.AdvancedFan?.dome?.options.length - 1 &&
                          styles.rightDivider
                        }
                         ${!roofHatchBoxActive && styles.disableText2}`}
                          key={item.key}
                          value={item.value}
                          onClick={() => changeRoofHatch(item.value, roofFan)}
                        >
                          {item?.key}
                        </div>
                      ))}
                    </div> */}
                    <div className={styles.selectStatelessContainerFan}>
                      {roofFan?.AdvancedFan?.dome?.options?.map((item) => (
                        <div
                          className={`${styles.selectOptions}
                            ${item.selected && roofFan?.AdvancedFan?.dome && styles.pillToggleButtonActive}
                            ${styles.statelessBtn}`}
                          key={item.key}
                          onClick={() => changeRoofHatch(item.value, roofFan)}
                        >
                          {item?.key}
                        </div>
                      ))}
                    </div>
                  </div>
                  <div
                    className={`${styles.hatchOption} ${styles.fanOption} ${
                      !roofHatchBoxActive && styles.disableText2
                    }`}
                  >
                    <p className={styles.fanText}>{roofFan?.AdvancedFan?.fanSpd?.title}</p>

                    <div className={styles.selectStatelessContainerFan}>
                      {roofFan?.AdvancedFan?.fanSpd?.options?.map((item) => (
                        <div
                          className={`${styles.selectOptions} ${
                            item.selected && roofFan?.AdvancedFan?.dome && styles.pillToggleButtonActive
                          }  ${styles.statelessBtn}`}
                          key={item.key}
                          onClick={() => changeFanSpeed(item.value, roofFan)}
                        >
                          {item?.key}
                        </div>
                      ))}
                    </div>
                  </div>
                  {/* <div
                    className={`${styles.hatchOption} ${styles.fanOption} ${
                      !roofHatchBoxActive && styles.disableText2
                    }`}
                  >
                    <p>Direction</p>
                    <div className={styles.selectContainer}>
                      {roofFan?.AdvancedFan?.direction?.options.map(
                        (item, ind) => (
                          <div
                            className={`${styles.selectOptions} ${
                              item.selected &&
                              roofFan?.AdvancedFan?.dome &&
                              styles.activeBtn
                            }
                        ${
                          ind !==
                            roofFan?.AdvancedFan?.direction?.options - 1 &&
                          styles.rightDivider
                        }
                         ${!roofHatchBoxActive && styles.disableText2}`}
                            key={item?.value}
                            value={item?.value}
                            selected={item.selected}
                            onClick={() =>
                              changeFanDirection(item.value, roofFan)
                            }
                          >
                            <ArrowUpBig
                              className={`${
                                item.key === "In" && styles.rotate
                              } ${styles.arrowIcon} ${
                                !roofHatchBoxActive && styles.disableIcon2
                              } `}
                            />
                            {item?.key}
                          </div>
                        )
                      )}
                    </div>
                  </div> */}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* {showModal === "speed" && (
        <Popup width="70%" height="30vh" top="50px" togglePopup={togglePopup}>
          <FanSpeedModal fanSpeed={fanSpeed} setFanSpeed={setFanSpeed} />
        </Popup>
      )}
      {showModal === "fan" && (
        <Popup width="70%" height="30vh" top="50px" togglePopup={togglePopup}>
          <FanModal fanStatus={fanStatus} setFanStatus={setFanStatus} />
        </Popup>
      )} */}

      {showSettingsModal && (
        <Popup width="50%" top="50px" closePopup={closeSettingModal}>
          <ClimateSettings handleClose={closeSettingModal} />
        </Popup>
      )}
      {/* {showScheduler && (
        <Popup width="45%" top="50px" togglePopup={toggleSchedular}>
          <Scheduler clearSchedule={clearCurrentSchedule} />
        </Popup>
      )} */}
    </DataContext.Provider>
  );
}

export default ClimateControl;
