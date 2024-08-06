import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../../../../context/AppContext";
import BackButton from "../../../../components/settings/back-button/BackButton";
import SettingRow from "../../../../components/settings/setting-row/SettingRow";
import TempController from "../../../../components/settings/temp-controller/TempController";
import { SETTINGS_LINKS } from "../../../../constants/CONST";
import { useFetch } from "../../../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../../../utils/api";

import styles from "./climate.module.css";

const FeatureClimateControl = () => {
  const navigate = useNavigate();
  const { pollingInterval } = useContext(AppContext);
  const { data, refreshDataImmediate } = useFetch(
    API_ENDPOINT.SETTING,
    LOCAL_ENDPOINT.SETTING,
    true,
    pollingInterval
  );
  const [displayInnerDetail, setDisplayInnerDetail] = useState(null);

  const climateData = data?.[0]?.tabs
    ?.filter((tab) => `${tab.name}` === SETTINGS_LINKS.FEATURES)[0]
    ?.details?.configuration?.filter(
      (config) => config.name === SETTINGS_LINKS.FEATURES_CLIMATE_CONTROL
    )[0]?.data[0];

  console.log("climateData?.configuration", climateData?.configuration);

  return (
    <>
      {!displayInnerDetail && (
        <>
          <div className={styles.header}>
            <div className={styles.backBtn}>
              <BackButton handler={() => navigate(-1)} />
            </div>
            <p className={styles.headingText}>{climateData?.title}</p>
          </div>

          {/* {featureData?.map((item, ind) => (
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
                          text={dat?.value?.version || dat?.value}
                          arrow
                          noBorder={arr.length - 1 === ind}
                          bottomText={dat?.subtext}
                        />
                      </div>
                    ))}
                  </div>
                </div>
              </React.Fragment>
            ))} */}
          {climateData?.configuration?.map((item, ind) => (
            <React.Fragment key={ind}>
              <div className={styles.itemContainer}>
                <p className={styles.containerHeading}>{item.title}</p>
                <div className={styles.contentContainer}>
                  {item?.items?.map((dat, ind, arr) => (
                    <div
                      key={ind}
                      onClick={() => {
                        dat?.data && setDisplayInnerDetail(dat);
                        dat?.items && setDisplayInnerDetail(dat);
                      }}
                    >
                      <SettingRow
                        name={dat?.title}
                        text={dat?.value?.version || dat?.value}
                        arrow={dat?.items?.length > 0 || dat?.data?.length > 0}
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
            <p className={styles.headingText}>{displayInnerDetail?.title}</p>
          </div>

          {displayInnerDetail.title === "Heat/Cool Min Delta" && (
            <div className={styles.itemContainer}>
              <TempController
                data={climateData?.configuration?.[0]?.items?.[0]}
                refreshDataImmediate={refreshDataImmediate}
              />
            </div>
          )}
          {displayInnerDetail.title === "Cool Differential Temperature" && (
            <div className={styles.itemContainer}>
              <TempController
                data={climateData?.configuration?.[0]?.items?.[1]}
                refreshDataImmediate={refreshDataImmediate}
              />
            </div>
          )}
          {displayInnerDetail.title === "Compressor Min Outdoor Temp" && (
            <div className={styles.itemContainer}>
              <TempController
                data={climateData?.configuration?.[0]?.items?.[2]}
                refreshDataImmediate={refreshDataImmediate}
              />
            </div>
          )}

          {displayInnerDetail?.title === "Temperature Alert" && (
            <>
              {climateData?.configuration?.[0]?.items?.[3]?.items?.map(
                (item, ind) => (
                  <React.Fragment key={ind}>
                    <div className={styles.itemContainer}>
                      <p className={styles.containerHeading}>{item?.title}</p>
                      <div className={styles.contentContainer}>
                        {item?.items?.map((dat, ind, arr) => (
                          <div key={ind}>
                            <SettingRow
                              name={dat?.title}
                              text={dat?.value?.version || dat?.value}
                              toggle={dat?.state}
                              refreshDataImmediate={refreshDataImmediate}
                              action={dat?.actions?.TOGGLE?.action}
                              toggleState={dat?.state?.onoff}
                              noBorder={arr.length - 1 === ind}
                            />
                          </div>
                        ))}
                      </div>
                      {item?.items?.[0]?.subtext && (
                        <p className={styles.containerSubInfo}>
                          {item?.items?.[0]?.subtext}
                        </p>
                      )}
                    </div>
                  </React.Fragment>
                )
              )}

              {climateData?.configuration?.[0]?.items?.[3]?.items?.[0]?.items?.map(
                (item, ind) => (
                  <React.Fragment key={ind}>
                    <div className={styles.itemContainer}>
                      <p className={styles.containerHeading}>{item?.title}</p>
                      <div className={styles.contentContainer}>
                        {item?.items?.map((dat, ind, arr) => (
                          <div key={ind}>
                            <SettingRow
                              name={dat?.title}
                              text={dat?.value?.version || dat?.value}
                              toggle={dat?.state}
                              refreshDataImmediate={refreshDataImmediate}
                              toggleState={dat?.state?.onoff}
                              noBorder={arr.length - 1 === ind}
                            />
                          </div>
                        ))}
                      </div>
                      {item?.items?.[0]?.subtext && (
                        <p className={styles.containerSubInfo}>
                          {item?.items?.[0]?.subtext}
                        </p>
                      )}
                    </div>
                  </React.Fragment>
                )
              )}
            </>
          )}

          {displayInnerDetail?.title === "Rain Sensor" && (
            <>
              <div className={styles.itemContainer}>
                <p className={styles.containerHeading}>
                  {displayInnerDetail?.title}
                </p>
                <div className={styles.contentContainer}>
                  {climateData?.configuration?.[1]?.items?.[0]?.items?.map(
                    (dat, ind, arr) => (
                      <div key={ind}>
                        <SettingRow
                          name={dat?.title}
                          text={dat?.value?.version || dat?.value}
                          toggle={dat?.state}
                          refreshDataImmediate={refreshDataImmediate}
                          action={dat?.actions?.TOGGLE?.action}
                          toggleState={dat?.state?.onoff}
                          noBorder={arr.length - 1 === ind}
                        />
                      </div>
                    )
                  )}
                </div>
              </div>
            </>
          )}
          {(displayInnerDetail?.title === "Furnace" ||
            displayInnerDetail?.title === "Air Conditioner" ||
            displayInnerDetail?.title === "Roof Hatch") && (
            <>
              {displayInnerDetail?.data?.map((item, ind) => (
                <React.Fragment key={ind}>
                  <div className={styles.itemContainer}>
                    <p className={styles.containerHeading}>{item.title}</p>
                    <div className={styles.contentContainer}>
                      {item?.data?.map((dat, ind, arr) => (
                        <div
                          key={ind}
                          onClick={() => {
                            dat?.data && setDisplayInnerDetail(dat);
                            dat?.items && setDisplayInnerDetail(dat);
                          }}
                        >
                          <SettingRow
                            name={dat?.title}
                            text={dat?.value?.version || dat?.value}
                            arrow={
                              dat?.items?.length > 0 || dat?.data?.length > 0
                            }
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
      )}
    </>
  );
};

export default FeatureClimateControl;
