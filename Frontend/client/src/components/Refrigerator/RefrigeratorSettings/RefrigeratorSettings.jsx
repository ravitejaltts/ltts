import React, { useContext, useEffect, useState } from "react";
import { AppContext } from "../../../context/AppContext";
import { Close } from "../../../assets/asset";
import { useFetch } from "../../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../../utils/api";
import RefridgeratorSettingDetail from "../RefridgeratorSettingDetail";
import RefridgeratorSettingRow from "../RefridgeratorSettingRow/RefridgeratorSettingRow";
import TemperatureAlerts from "../TemperatureAlerts";
import { DETAIL_MODE, MAIN_MODE, MANUFACTURE_TITLE, SETTING_TITLE } from "./constants";
import styles from "./index.module.css";

const RefrigeratorSettings = ({ handleClose, parentRefetch }) => {
  const { pollingInterval } = useContext(AppContext);
  const { data, refreshDataImmediate: refeshParentData } = useFetch(
    API_ENDPOINT.REFRIDGERATOR_SETTING,
    LOCAL_ENDPOINT.REFRIDGERATOR_SETTING,
    true,
    pollingInterval,
  );
  // const data = refSettings;
  // console.log("sett", data);
  const [currentMode, setCurrentMode] = useState(MAIN_MODE);
  const [detailData, setDetailData] = useState({});

  const openDetail = (item) => {
    setDetailData(item);
    setCurrentMode(DETAIL_MODE);
  };
  useEffect(() => {
    parentRefetch(false);
    return () => {
      parentRefetch(true);
    };
  }, []);

  return (
    <div className={styles.settings}>
      {currentMode === "fridge-control" ? (
        <TemperatureAlerts
          data={data?.configuration[0]}
          setCurrentMode={setCurrentMode}
          currentMode="fridge-control"
          refeshParentData={refeshParentData}
        />
      ) : currentMode === "freezer-control" ? (
        <TemperatureAlerts
          data={data?.configuration[1]}
          setCurrentMode={setCurrentMode}
          currentMode="freezer-control"
          refeshParentData={refeshParentData}
        />
      ) : currentMode === DETAIL_MODE ? (
        <RefridgeratorSettingDetail data={detailData} setCurrentMode={setCurrentMode} />
      ) : (
        <div className={styles.max}>
          <div className={styles.header}>
            <Close onClick={handleClose} className={styles.closeIcon} />
            <p className={styles.heading}>{data?.title || SETTING_TITLE}</p>
          </div>
          {data?.configuration?.length &&
            data?.configuration?.map(({ items, title }, i) => {
              return (
                <div
                  onClick={() => {
                    if (i === 0) {
                      setCurrentMode("fridge-control");
                    } else if (i === 1) {
                      setCurrentMode("freezer-control");
                    }
                  }}
                  className={styles.infoContainer}
                  style={{ marginTop: "20px" }}
                >
                  <RefridgeratorSettingRow
                    name={title || "Title"}
                    text={items[0]?.Simple?.onOff === 1 ? "On" : "Off"}
                    arrow
                    noBorder={true}
                  />
                </div>
              );
            })}
          {/* {data?.configuration?.length && (
            <div
              onClick={() => setCurrentMode(CONTROL_MODE)}
              className={styles.infoContainer}
              style={{ marginTop: "20px" }}
            >
              <RefridgeratorSettingRow
                name={data?.configuration[0]?.items[0]?.title}
                text={
                  data?.configuration[0]?.items[0]?.Simple?.onOff === 1
                    ? "On"
                    : "Off"
                }
                arrow
                noBorder={true}
              />
            </div>
          )} */}
          <p className={styles.infoText}>{data?.information?.title || MANUFACTURE_TITLE}</p>
          <div className={styles.infoContainer}>
            {data?.information?.[0]?.items?.[0]?.sections?.map((item, index, arr) => (
              <div key={index} onClick={() => openDetail(item)}>
                <RefridgeratorSettingRow name={item?.title} arrow noBorder={index === arr.length - 1} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default RefrigeratorSettings;
