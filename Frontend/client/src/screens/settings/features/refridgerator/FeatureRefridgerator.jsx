import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../../../../context/AppContext";
import BackButton from "../../../../components/settings/back-button/BackButton";
import FridgeController from "../../../../components/settings/fridge-controller/FridgeController";
import SettingRow from "../../../../components/settings/setting-row/SettingRow";
import { SETTINGS_LINKS } from "../../../../constants/CONST";
import { useFetch } from "../../../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../../../utils/api";

import styles from "./refridgerator.module.css";

const FeatureRefridgerator = () => {
  const navigate = useNavigate();
  const { pollingInterval } = useContext(AppContext);
  const { data, refreshDataImmediate } = useFetch(API_ENDPOINT.SETTING, LOCAL_ENDPOINT.SETTING, true, pollingInterval);
  const [displayInnerDetail, setDisplayInnerDetail] = useState(null);

  // const fridgeData =
  //   data?.data?.[2]?.data?.[0]?.data?.configuration?.[5]?.configuration;

  const refrigeratorData = data?.[0]?.tabs
    ?.filter((tab) => `${tab.name}` === SETTINGS_LINKS.FEATURES)[0]
    ?.details?.configuration?.filter((config) => config.name === SETTINGS_LINKS.FEATURES_REFRIDGERATOR)[0];
  console.log(refrigeratorData?.items?.[0]?.item);

  return (
    <>
      {!displayInnerDetail && (
        <>
          <div className={styles.header}>
            <div className={styles.backBtn}>
              <BackButton handler={() => navigate(-1)} />
            </div>
            <p className={styles.headingText}>{refrigeratorData?.title}</p>
          </div>

          {refrigeratorData?.items?.map((item, ind) => (
            <React.Fragment key={ind}>
              <div className={styles.itemContainer}>
                <p className={styles.containerHeading}>{item.title}</p>
                <div className={styles.contentContainer}>
                  {item?.item?.map((dat, ind, arr) => {
                    if (dat?.type === "SIMPLE_ONOFF") {
                      return (
                        <div onClick={() => setDisplayInnerDetail(item)}>
                          <SettingRow
                            name={dat?.title}
                            arrow
                            text={dat?.state?.onoff ? "On" : "Off"}
                            toggleState={dat?.Simple?.onOff}
                            noBorder={ind === arr.length - 1}
                            refreshDataImmediate={refreshDataImmediate}
                          />
                        </div>
                      );
                    }
                  })}
                  {item?.data?.map((dat, ind, arr) => (
                    <SettingRow
                      name={dat?.title}
                      text={dat?.value}
                      noBorder={arr.length - 1 === ind}
                      action={dat?.actions?.TAP?.action}
                      refreshDataImmediate={refreshDataImmediate}
                    />
                  ))}
                </div>
              </div>
            </React.Fragment>
          ))}
        </>
      )}
      {displayInnerDetail && (
        <>
          <div className={styles.header}>
            <div className={styles.backBtn}>
              <BackButton handler={() => setDisplayInnerDetail(null)} />
            </div>
            <p className={styles.headingText}>{displayInnerDetail.title}</p>
          </div>

          <div className={styles.itemContainer}>
            <FridgeController data={refrigeratorData?.items?.[0]?.item} refreshDataImmediate={refreshDataImmediate} />
          </div>
        </>
      )}
    </>
  );
};

export default FeatureRefridgerator;
