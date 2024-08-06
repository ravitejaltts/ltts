import axios from "axios";
import { useContext, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../../context/AppContext";
import { BackIcon, RoundAlert, SettingsIcon } from "../../assets/asset";
import { SlideOutHeader, SlideOutInfo, SlideOutWarning } from "../../assets/assets";
import MultiFunctionalButton from "../../components/common/MultiFunctionButton";
import Popup from "../../components/common/Popup/Popup";
import SlideOutsLegalDisclaimer from "../../components/slide-outs/slide-outs-legal-disclaimer/SlideOutsLegalDisclaimer";
import SlideOutsSafetyMessages from "../../components/slide-outs/slide-outs-safety-messages/SlideOutsSafetyMessages";
import SlideOutsSettings from "../../components/slide-outs/slide-outs-settings/SlideOutsSettings";
import { useFetch } from "../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../utils/api";
import styles from "./slide-outs.module.css";
import { getIcon } from "../awning/Awning";

const iconObj = {
  ALERT: <SlideOutWarning />,
  INFO: <SlideOutInfo />,
  DEFAULT: <SlideOutInfo />,
};

const SlideOuts = () => {
  const { pollingInterval, setSideBarShow } = useContext(AppContext);
  const { data: slideOutData, refreshDataImmediate } = useFetch(
    API_ENDPOINT.SLIDE_OUT_SCREEN,
    LOCAL_ENDPOINT.SLIDE_OUT_SCREEN,
    true,
    pollingInterval,
  );

  const navigate = useNavigate();
  const [showWaringScreen, setShowWarningScreen] = useState(true);
  const [allMessages, setAllMessages] = useState(false);
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [showLegal, setShowLegal] = useState(false);
  const [deadmanActive, setDeadmanActive] = useState(null);

  const errorApiRef = useRef(false);

  useEffect(() => {
    if (slideOutData?.hideSidebar) {
      setSideBarShow(slideOutData?.hideSidebar);
    }
  }, [slideOutData]);

  const openSettingModal = () => {
    setShowSettingsModal(true);
  };
  const closeSettingModal = () => {
    setShowSettingsModal(false);
  };

  const showSafetyMessages = () => {
    // navigate("/home/awningSafetyMessages");
  };

  const handleHold = (actionObj, value) => {
    axios
      .put(
        actionObj?.action?.href,
        {
          mode: value,
        },
        {
          headers: {
            "origin-ts": Date.now(),
          },
        },
      )
      .then((res) => {})
      .catch((err) => {
        if (err?.response?.status === 423) {
          setDeadmanActive(null);
        }
      });
  };
  const handleRelease = (actionObj) => {
    errorApiRef.current = true;
    axios
      .put(actionObj?.action?.href, {
        ...actionObj?.action?.param,
      })
      .then(() => {
        errorApiRef.current = false;
      })
      .catch(() => {
        setTimeout(() => {
          handleRelease(actionObj);
        }, 1000);
      });
  };

  if (showLegal) {
    return <SlideOutsLegalDisclaimer data={showLegal} handleClose={() => setShowLegal(false)} />;
  }

  const closeMessageScreen = () => {
    setAllMessages(false);
  };

  const lockOutData = slideOutData?.slideOuts?.[0]?.lockouts;
  return (
    <>
      {(showWaringScreen || allMessages) && (
        <SlideOutsSafetyMessages
          simple={allMessages}
          simpleCb={closeMessageScreen}
          successCb={() => setShowWarningScreen(false)}
          fetchString={"SLIDE_OUT_WARNING"}
        />
      )}

      {!showWaringScreen && (
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
                <div className={styles.settingsContainer} onClick={openSettingModal}>
                  <SettingsIcon />
                </div>
              </div>
              <h2 className={styles.lightingHeadingText}>
                {slideOutData?.overview?.title?.split(" ")?.map((word, ind) => (
                  <p className="m-0" key={ind}>
                    {word}
                  </p>
                )) || "Slide-Outs"}
              </h2>
              {/* <h4 className={styles.outdoorTemp}></h4> */}
            </div>

            <div className={styles.infoBoxContainer}>
              {slideOutData?.overview?.warnings?.map((messages, ind) => (
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
                        <p onClick={() => setAllMessages(true)}>{messages?.footer?.title}</p>
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
                <div className={`${styles.rowLayout} `}>
                  <RoundAlert className={styles.roundAlert} />
                  <div className={styles.centerTextDiv}>
                    <h2 className={`${styles.lightMasterText} `}>{lockout?.title}</h2>
                    <p
                      className={`${styles.lightsOnText} `}
                      dangerouslySetInnerHTML={{
                        __html: lockout?.subtext?.replace(
                          "{timer}",
                          `<span className="dangerour">${lockout?.state?.timer}</span>`,
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
              ))}
              {slideOutData?.slideOuts?.map((data) => (
                <div key={data?.title}>
                  <div className={`${styles.rowLayout} ${!!lockOutData?.length && styles.disableRightTop}`}>
                    {/* {data?.enabled ? ( */}
                    <SlideOutHeader
                    // className={`${!tempBoxActive && styles.disableIcon}`}
                    />
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
                      <div className={styles.topBtns}>
                        {data?.options?.map((buttons, ind) => {
                          let id = buttons?.key ?? ind;
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
                              onReleaseCb={() => handleRelease(data?.actions?.RELEASE)}
                              longPressCallback={() => handleHold(data?.actions?.HOLD, buttons?.value)}
                              holdDelayTime={data?.holdDelayMs}
                              apiCallIntervalTime={data?.intervalMs}
                              animateColor="#4c85a9"
                              handleDeadman={setDeadmanActive}
                              deadmanState={deadmanActive}
                            >
                              <div className={`${styles.topBtn} ${!buttons?.enabled && styles.disabled}`}>
                                <p className={styles.btnTitle}>{buttons?.key}</p>
                                <p>{buttons?.subtext}</p>
                              </div>
                            </MultiFunctionalButton>
                          );
                        })}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          {showSettingsModal && (
            <Popup width="50%" top="50px" closePopup={closeSettingModal}>
              <SlideOutsSettings setShowLegal={setShowLegal} handleClose={closeSettingModal} />
            </Popup>
          )}
        </div>
      )}
    </>
  );
};

export default SlideOuts;
