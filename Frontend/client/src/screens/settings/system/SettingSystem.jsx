import React, { useEffect, useState } from "react";
import { useLocation, useNavigate, useOutletContext } from "react-router-dom";
import axios from "axios";
import SettingRow from "../../../components/settings/setting-row/SettingRow";
import { SETTINGS_LINKS } from "../../../constants/CONST";
import styles from "./system.module.css";
import BackButton from "../../../components/settings/back-button/BackButton";
import SystemDateTime from "./date-time/SystemDateTime";
import SystemLocation from "./location/SystemLocation";
import SystemConfig from "./configuration/SystemConfig";
import SystemMasterReset from "./master-reset/SystemMasterReset";
import SystemErrorLogs from "./error-logs/SystemErrorLogs";
import SystemDiagnostics from "./system-diagnostics/SystemDiagnostics";

const SettingSystem = () => {
  const location = useLocation();
  const [setActiveTab, data] = useOutletContext();
  const [subPage, setSubPage] = useState(null);
  const [innerSubpage, setInnerSubpage] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    setActiveTab(location?.pathname);
  }, []);

  const SUBPAGES = {
    DATE_TIME: "Date and Time",
    TEMP: null,
    LOCATION: "Location",
    ERROR_LOGS: "Error Log",
    CONFIGURATION: "User Configuration Backup",
    MASTER_RESET: "Master Reset",
    SYSTEM_DIAGNOSE: "System Diagnostics",
  };

  const settingData = data?.[0]?.tabs?.filter((tab) => `${tab.name}` === SETTINGS_LINKS.SYSTEM)?.[0]?.details;

  function callRestartApi(data) {
    data?.actions?.TAP?.action?.href && axios.put(data?.actions?.TAP?.action?.href, { onoff: 1 });
  }

  const handleBackClick = (sub) => {
    if (innerSubpage?.title !== "Timezone") {
      setSubPage(null);
    } else {
      setInnerSubpage("");
    }
  };

  const handleTitleClicked = () => {
    axios.put("/api/system/features/settings/fcp", {});
  };
  return (
    <>
      {!subPage && (
        <React.Fragment>
          <div className={styles.header}>
            <p
              className={styles.headingText}
              onClick={() => {
                handleTitleClicked();
              }}
            >
              {settingData?.title || "System"}
            </p>
          </div>
          {settingData?.data?.map((item, ind) => (
            <React.Fragment key={ind}>
              {item?.type !== "Button" ? (
                <div className={styles.itemContainer}>
                  <p className={styles.containerHeading}>{item?.title}</p>
                  <div className={styles.contentContainer}>
                    {item?.configuration?.map((dat, ind, arr) => (
                      <div
                        key={ind}
                        onClick={() => {
                          if (dat?.type === "SETTINGS_LIST_ITEM_NAV_REDIRECT") {
                            navigate(`${dat?.actions?.TAP?.action?.href}`);
                          } else {
                            setSubPage(dat);
                          }
                        }}
                      >
                        <SettingRow
                          name={dat?.title}
                          arrow
                          text={dat?.value?.version || dat?.value}
                          noBorder={arr.length - 1 === ind}
                          bottomText={dat?.subtext}
                        />
                      </div>
                    ))}
                    {item?.data?.map((dat, ind, arr) => (
                      <div key={ind} onClick={() => setSubPage(dat)}>
                        <SettingRow
                          name={dat?.title}
                          arrow
                          text={dat?.value?.version || dat?.value}
                          noBorder={arr.length - 1 === ind}
                          bottomText={dat?.subtext}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <button className="resetBtn" onClick={() => callRestartApi(item)}>
                  {item?.title}
                </button>
              )}
            </React.Fragment>
          ))}
        </React.Fragment>
      )}

      {subPage && (
        <React.Fragment>
          <div className={styles.header}>
            <div className={styles.backBtn}>
              <BackButton handler={handleBackClick} />
            </div>
            <p className={styles.headingText}>{subPage?.title}</p>
          </div>
          {subPage?.title === SUBPAGES.DATE_TIME && (
            <SystemDateTime
              data={settingData?.data?.[0]?.configuration?.[0]}
              innerSubpage={innerSubpage}
              setInnerSubpage={setInnerSubpage}
            />
          )}

          {subPage?.title === SUBPAGES.LOCATION && (
            <SystemLocation data={settingData?.data?.[1]?.configuration[0]?.data?.[0]?.data} />
            // <SystemLocation data={subPage?.data?.[0]?.data} />
          )}
          {subPage?.title === SUBPAGES.ERROR_LOGS && (
            <SystemErrorLogs data={settingData?.data[2]?.configuration[0]?.data?.[0]?.data?.[0]} />
            // <SystemErrorLogs data={subPage?.data?.[0]?.data?.[0]} />
          )}
          {subPage?.title === SUBPAGES.CONFIGURATION && (
            <SystemConfig data={subPage?.data[0]?.data} />
            // <SystemConfig data={subPage?.data[0]?.data} />
          )}
          {subPage?.title === SUBPAGES.MASTER_RESET && (
            // <SystemMasterReset
            //   data={subPage?.configuration?.[0]?.data?.[0]?.data}
            // />
            <SystemMasterReset data={settingData?.data[3]?.configuration[0]?.configuration?.[0]?.data?.[0]?.data} />
          )}
          {subPage?.title === SUBPAGES.SYSTEM_DIAGNOSE && (
            <SystemDiagnostics data={settingData?.data[4]?.configuration[0]?.data[0]?.data} />
          )}
        </React.Fragment>
      )}
    </>
  );
};

export default SettingSystem;
