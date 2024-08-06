import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../../../../context/AppContext";
import BackButton from "../../../../components/settings/back-button/BackButton";
import SettingRow from "../../../../components/settings/setting-row/SettingRow";
import { SETTINGS_LINKS } from "../../../../constants/CONST";
import { useFetch } from "../../../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../../../utils/api";
import styles from "./inverter.module.css";

const FeatureInverter = () => {
  const navigate = useNavigate();
  const { pollingInterval } = useContext(AppContext);
  const { data } = useFetch(API_ENDPOINT.SETTING, LOCAL_ENDPOINT.SETTING, true, pollingInterval);
  const [displayInnerDetail, setDisplayInnerDetail] = useState(null);

  const inverterData = data?.[0]?.tabs
    ?.filter((tab) => `${tab.name}` === SETTINGS_LINKS.FEATURES)[0]
    ?.details?.configuration?.filter((config) => config.name === SETTINGS_LINKS.FEATURES_INVERTER)[0]?.data[0];

  return (
    <>
      {!displayInnerDetail && (
        <>
          <div className={styles.header}>
            <div className={styles.backBtn}>
              <BackButton handler={() => navigate(-1)} />
            </div>
            <p className={styles.headingText}>{inverterData?.title}</p>
          </div>

          {inverterData?.data?.map((item, ind) => (
            <React.Fragment key={ind}>
              <div className={styles.itemContainer}>
                <p className={styles.containerHeading}>{item.title}</p>
                <div className={styles.contentContainer}>
                  {item?.data?.map((dat, ind, arr) => (
                    <div
                      key={ind}
                      onClick={() => {
                        dat?.data && setDisplayInnerDetail(dat);
                      }}
                    >
                      <SettingRow
                        name={dat?.title}
                        arrow={dat?.data}
                        text={dat?.value}
                        noBorder={arr.length - 1 === ind}
                        bottomText={dat?.subtext}
                      />
                    </div>
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
          {displayInnerDetail?.data?.map((item, ind) => (
            <React.Fragment key={ind}>
              <div className={styles.itemContainer}>
                <p className={styles.containerHeading}>{item.title}</p>
                <div className={styles.contentContainer}>
                  {item?.data?.map((dat, ind, arr) => (
                    <div key={ind}>
                      <SettingRow
                        name={dat?.title}
                        text={dat?.value}
                        noBorder={arr.length - 1 === ind}
                        bottomText={dat?.subtext}
                      />
                    </div>
                  ))}
                </div>
              </div>
            </React.Fragment>
          ))}
        </>
      )}
    </>
  );
};

export default FeatureInverter;
