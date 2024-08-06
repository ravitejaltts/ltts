import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../../../../context/AppContext";
import BackButton from "../../../../components/settings/back-button/BackButton";
import SettingRow from "../../../../components/settings/setting-row/SettingRow";
import { SETTINGS_LINKS } from "../../../../constants/CONST";
import { useFetch } from "../../../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../../../utils/api";
import styles from "./pet.module.css";
import LegalDisclamer from "../../../../components/settings/legal-disclamer/LegalDisclamer";

const FeaturePetMonitor = () => {
  const navigate = useNavigate();
  const { pollingInterval } = useContext(AppContext);
  const { data, refreshDataImmediate } = useFetch(API_ENDPOINT.SETTING, LOCAL_ENDPOINT.SETTING, true, pollingInterval);
  const [displayInnerDetail, setDisplayInnerDetail] = useState(null);

  const petData = data?.[0]?.tabs
    ?.filter((tab) => `${tab.name}` === SETTINGS_LINKS.FEATURES)[0]
    ?.details?.configuration?.filter((config) => config.name === SETTINGS_LINKS.FEATURES_PET)[0];
  console.log(displayInnerDetail);
  return (
    <>
      {!displayInnerDetail && (
        <>
          <div className={styles.header}>
            <div className={styles.backBtn}>
              <BackButton handler={() => navigate(-1)} />
            </div>
            <p className={styles.headingText}>{petData?.title}</p>
          </div>

          {petData?.items?.map((item, ind) => (
            <React.Fragment key={ind}>
              <div className={styles.itemContainer}>
                <p className={styles.containerHeading}>{item.title}</p>
                <div className={styles.contentContainer}>
                  {item?.data?.map((dat, ind, arr) => (
                    <div
                      key={ind}
                      onClick={() => {
                        dat?.data?.length >= 1 && setDisplayInnerDetail(dat);
                      }}
                    >
                      <SettingRow
                        name={dat?.title}
                        arrow={dat?.data?.length >= 1}
                        noBorder={arr.length - 1 === ind}
                        text={dat?.subtext}
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
        <LegalDisclamer data={displayInnerDetail?.data?.[0]?.data?.[0]} close={() => setDisplayInnerDetail(null)} />
      )}
    </>
  );
};

export default FeaturePetMonitor;
