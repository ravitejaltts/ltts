import axios from "axios";
import { useContext, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../../context/AppContext";
import { AwningLightIcon, AwningPositionIcon, BackIcon, RoundAlert, SettingsIcon } from "../../assets/asset";
import { SlideOutInfo, SlideOutWarning, WarningIcon } from "../../assets/assets";
import AwningLegalDisclaimer from "./awning-legal-disclaimer/AwningLegalDisclaimer";
import AwningSlider from "./awning-slider/AwningSlider";
import MultiFunctionalButton from "../../components/common/MultiFunctionButton";
import Popup from "../../components/common/Popup/Popup";
import SimpleSwitch from "../../components/common/SimpleSwitch/SimpleSwitch";
import SlideOutsSafetyMessages from "../../components/slide-outs/slide-outs-safety-messages/SlideOutsSafetyMessages";
import { useFetch } from "../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../utils/api";
import AwningSettings from "./awning-settings/AwningSettings";
import styles from "./awning.module.css";

export const getIcon = (title) => {
  if (title === "Caution") {
    return <WarningIcon />;
  }

  if (title === "Danger" || title === "Warning") {
    return <SlideOutWarning />;
  }
  return <SlideOutInfo />;
};

const BACK_API = "/api/movables/aw/1/state";
const BACK_PARAMS = {
  mode: 0,
};

function Awning() {
  const navigate = useNavigate();
  const { pollingInterval, setSideBarShow } = useContext(AppContext);
  const { data, refreshDataImmediate } = useFetch(
    API_ENDPOINT.AWNING_SCREEN,
    LOCAL_ENDPOINT.AWNING_SCREEN,
    true,
    pollingInterval,
  );
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [disclaimer, setDisclaimer] = useState(false);
  const [showWaringScreen, setShowWarningScreen] = useState(true);
  const [allMessages, setAllMessages] = useState(false);

  const [deadmanActive, setDeadmanActive] = useState(null);

  const errorApiRef = useRef(false);
  const stopThenNavigate = (path) => {
    // Send API to stop
    axios.put(BACK_API, {
      ...BACK_PARAMS,
    });
    // TODO: Need to get this from the API
    navigate(path);
  };

  useEffect(() => {
    if (data?.hideSidebar) {
      setSideBarShow(data?.hideSidebar);
    }
  }, [data]);

  const getSwitchesCount = () => {
    return data?.switches?.length || 0;
  };

  const openSettingModal = () => {
    setShowSettingsModal(true);
  };
  const closeSettingsModal = () => {
    setShowSettingsModal(false);
  };

  const showSafetyMessages = () => {
    // navigate("/home/awningSafetyMessages");
  };

  // console.log(data);
  const closeMessageScreen = () => {
    setAllMessages(false);
  };

  const handleHold = (actionObj) => {
    // console.log("actionhold", actionObj);
    if (actionObj?.action?.href) {
      axios
        .put(actionObj?.action?.href, {
          ...actionObj?.action?.param,
        })
        .then(() => {
          refreshDataImmediate();
        })
        .catch((err) => {
          if (err?.response?.status === 423) {
            setDeadmanActive(null);
          }
        });
    }
  };
  const handleRelease = (actionObj) => {
    // console.log("actionrelease", actionObj);

    if (actionObj?.action?.href) {
      errorApiRef.current = true;
      axios
        .put(actionObj?.action?.href, {
          ...actionObj?.action?.param,
        })
        .then(() => {
          errorApiRef.current = false;
          refreshDataImmediate();
        })
        .catch(() => {
          setTimeout(() => {
            handleRelease(actionObj);
          }, 1000);
        });
    }
  };

  const handlePress = (actionObj) => {
    // console.log("Heasdlasd", actionObj);
    if (actionObj?.action?.href) {
      axios
        .put(
          actionObj?.action?.href,
          {
            ...actionObj?.action?.param,
          },
          {
            headers: {
              "origin-ts": Date.now(),
            },
          },
        )
        .then(() => {
          refreshDataImmediate();
        })
        .catch((err) => {
          if (err?.response?.status === 423) {
            setDeadmanActive(null);
          }
        });
    }
  };
  const lockOutData = data?.awnings?.[0]?.lockouts;

  return (
    <>
      {(showWaringScreen || allMessages) && (
        <SlideOutsSafetyMessages
          simple={allMessages}
          simpleCb={closeMessageScreen}
          successCb={() => setShowWarningScreen(false)}
          fetchString="AWNING_WARNING"
        />
      )}
      {!showWaringScreen && (
        <div className={styles.mainContainer}>
          <div className={styles.leftDiv}>
            <div>
              <div className={styles.leftDivTop}>
                <div className={styles.backNav} onClick={() => stopThenNavigate(-1)}>
                  <div className={styles.backContainer}>
                    <BackIcon />
                  </div>
                  <p className={styles.backText}>Back</p>
                </div>
                <div className={styles.settingsContainer} onClick={openSettingModal}>
                  <SettingsIcon />
                </div>
              </div>
              <h2 className={styles.lightingHeadingText}>
                {data?.overview?.title?.split(" ")?.map((word, ind) => (
                  <p className="m-0" key={ind}>
                    {word}
                  </p>
                )) || "Awning"}
              </h2>
              {/* <h4 className={styles.outdoorTemp}></h4> */}
            </div>

            <div className={styles.infoBoxContainer}>
              {data?.overview?.warnings?.map((messages, ind) => (
                <div key={ind} className={styles.leftBottomContainer} onClick={showSafetyMessages}>
                  <div className={styles.leftBottomDiv}>
                    <div className={styles.warningCaution}>
                      {getIcon(messages?.title)}
                      {/* {iconObj?.[messages?.type || "DEFAULT"]} */}
                      <p className={styles.msgTitle}> {messages?.title}</p>
                    </div>
                    <p className={styles.msgSubText}>{messages?.subtext}</p>
                    {messages?.footer && (
                      <div className={styles.allMessages}>
                        <span onClick={() => setAllMessages(true)}>{messages?.footer?.title}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
          {/* right div */}
          <div className={styles.mainRight}>
            <div className={styles.rightDiv}>
              {lockOutData?.map((lockout, ind) => (
                <div className={`${styles.rowLayout} `} key={ind}>
                  <RoundAlert className={styles.roundAlert} />
                  <div className={styles.centerTextDiv}>
                    <h2 className={`${styles.lightMasterText} `}>{lockout?.title}</h2>
                    <p
                      className={`${styles.lightsOnText} `}
                      dangerouslySetInnerHTML={{
                        __html: lockout?.subtext?.replace("{timer}", `<span>${lockout?.state?.timer}</span>`),
                      }}
                    >
                      {/* {lockoutsArray[0]?.subtext?.replace(
                      "{timer}",
                      lockoutsArray[0]?.state?.timer
                    )} */}
                    </p>
                  </div>
                </div>
              ))}
              {data?.awnings?.map((data, ind) => (
                <div key={ind}>
                  <div className={`${styles.rowLayout} ${!!lockOutData?.length && styles.disableRightTop}`}>
                    {/* {data?.enabled ? ( */}
                    <AwningPositionIcon />
                    {/* className={`${!tempBoxActive && styles.disableIcon}`} */}

                    {/* ) : (
                    <RoundAlert />
                  )} */}
                    <div className={styles.centerTextDivTop}>
                      <h2 className={`${styles.lightMasterText} ${!!lockOutData?.length && styles.disableText}`}>
                        {data?.title}
                      </h2>
                      <p className={`${styles.lightsOnText} ${!!lockOutData?.length && styles.disableText}`}>
                        {data?.subtext}
                      </p>
                    </div>
                    {/* <div className={styles.onTop}>
                <Switch
                  onOff={thermostatData?.master?.Simple?.onOff}
                  action={thermostatData?.master?.action_default?.action}
                  refreshParentData={refreshDataImmediate}
                />
              </div> */}
                  </div>
                  <div className={styles.rightBottomDiv}>
                    <div className={styles.rightInnerContainer}>
                      {data?.switches?.length === 1 && (
                        <div
                          className={styles.priorityOuter}
                          onTouchStart={() => {
                            handlePress(data?.switches?.[0]?.actions?.PRESS);
                          }}
                        >
                          <div className={styles.priorityInner}>
                            <span className={styles.priorityClose}>X</span>
                            <span className={styles.priorityText}>Stop</span>
                          </div>
                        </div>
                      )}
                      {data?.switches?.length > 1 &&
                        [...Array(getSwitchesCount() / 2 >= 1 ? getSwitchesCount() / 2 : 1).keys()].map((num) => (
                          <div className={styles.topBtns} key={num}>
                            {data?.switches?.slice(num * 2, num * 2 + 2)?.map((buttons, ind) => {
                              const id = (buttons?.title || "") + ind;
                              return (
                                <MultiFunctionalButton
                                  key={id}
                                  id={id}
                                  disabled={
                                    !data?.enabled ||
                                    !buttons?.enabled ||
                                    errorApiRef.current ||
                                    (deadmanActive !== null && deadmanActive !== id)
                                  }
                                  onReleaseCb={() => handleRelease(buttons?.actions?.RELEASE)}
                                  longPressCallback={() => handleHold(buttons?.actions?.HOLD)}
                                  onClickCb={() => {
                                    handlePress(buttons?.actions?.PRESS);
                                  }}
                                  holdDelayTime={buttons?.holdDelayMs}
                                  apiCallIntervalTime={buttons?.intervalMs}
                                  animateColor="#4c85a9"
                                  handleDeadman={setDeadmanActive}
                                  deadmanState={deadmanActive}
                                >
                                  <div
                                    className={`${styles.topBtn} ${!buttons?.enabled && styles.disabled} ${
                                      data?.switches?.length === 1 && styles.stopSign
                                    } `}
                                  >
                                    {data.switches?.length === 1 && <span className={styles.priorityClose}>X</span>}
                                    <p className={styles.btnTitle}>
                                      <p>{buttons?.title}</p>
                                      <p>{buttons?.subtext}</p>
                                    </p>
                                  </div>
                                </MultiFunctionalButton>
                              );
                            })}
                          </div>
                        ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
            {data?.awnings?.[0]?.awningLights?.map((lights, ind) => (
              <div className={styles.rightDiv} key={ind}>
                <div className={styles.rowLayout}>
                  <AwningLightIcon />
                  <div className={styles.centerTextDiv}>
                    <h2 className={`${styles.lightMasterText}`}>{lights?.title}</h2>
                    <p className={`${styles.lightsOnText}`}>{lights?.subtext}</p>
                  </div>
                  <div className={styles.onTop}>
                    <SimpleSwitch
                      onOff={lights?.state?.onOff}
                      extraPayload={{ ...lights?.state }}
                      toggleAction={lights?.action_default?.action}
                      refreshDataImmediate={refreshDataImmediate}
                    />
                  </div>
                </div>
                <div className={styles.rightBottomDiv}>
                  <div className={styles.awningLightContainer}>
                    <AwningSlider data={lights} refresh={refreshDataImmediate} />
                  </div>
                </div>
              </div>
            ))}
          </div>
          {showSettingsModal && (
            <Popup width="50%" top="50px" closePopup={closeSettingsModal}>
              <AwningSettings setDisclaimer={setDisclaimer} handleClose={closeSettingsModal} />
            </Popup>
          )}
          {disclaimer && <AwningLegalDisclaimer data={disclaimer} closeCb={() => setDisclaimer(false)} />}
        </div>
      )}
    </>
  );
}

export default Awning;
