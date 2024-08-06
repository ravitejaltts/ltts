import React, { useState } from "react";
import axios from "axios";
import { useFetch } from "../../../hooks/useFetch";
import { BackIcon, Close } from "../../../assets/asset";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../../utils/api";
import DetailRow from "../../../components/common/detail-row/DetailRow";
import SensitivityController from "../../../components/common/sensitivity-controller/SensitivityController";
import styles from "./awningSettings.module.css";

function AwningSettings({ handleClose, setDisclaimer }) {
  const { data: settingsData, refreshDataImmediate: toggleRefresh } = useFetch(
    API_ENDPOINT.AWNING_SETTTINGS,
    LOCAL_ENDPOINT.AWNING_SETTTINGS,
    false,
  );
  const [itemToShow, setItemToShow] = useState(null);
  const [unitDetailShow, setUnitDetailShow] = useState(null);
  const [windSensorSetting, setWindSensorSetting] = useState(false);

  const handleReset = (actionData) => {
    if (actionData?.TAP?.action?.href) {
      axios.put(actionData?.TAP?.action?.href).then(() => toggleRefresh());
    }
  };

  if (windSensorSetting) {
    return (
      <div className={styles.settings}>
        <div className={styles.header}>
          <div className={styles.back} onClick={() => setWindSensorSetting(null)}>
            <BackIcon />
            <h2>Back</h2>
          </div>
          <p className={styles.heading}>{settingsData?.data?.[0]?.title}</p>
        </div>
        {settingsData?.data?.[0]?.data?.map((data, ind) => (
          <React.Fragment key={ind}>
            {data?.type === "SECTIONS_LIST" && (
              <>
                <p className={styles.infoText}>{data?.title}</p>
                <div className={styles.infoContainer}>
                  {data?.data?.map((subdata, sindex) => (
                    <div key={sindex} onClick={() => setItemToShow()}>
                      <DetailRow
                        name={subdata?.title}
                        toggle
                        toggleState={subdata?.state?.onOff}
                        toggleAction={subdata?.actions?.TOGGLE?.action}
                        refreshDataImmediate={toggleRefresh}
                        noBorder
                      />
                    </div>
                  ))}
                </div>
                <p className={styles.windSensorSubText}>{data?.footer}</p>
              </>
            )}

            {data?.type === "simpleSlider" && data?.state.mtnSenseOnOff === 1 && (
              <div className={styles.sensitivityContainer}>
                <p className={styles.windSensorSubTextB}>{data?.title}</p>
                <div className={styles.controllerBox}>
                  <SensitivityController data={data} refresh={toggleRefresh} />
                </div>
                <p className={styles.windSensorSubText}>{data?.footer}</p>
              </div>
            )}
            {data?.type === "BUTTON" && (
              <button type="button" className={styles.restoreBtn} onClick={() => handleReset(data?.actions)}>
                {data?.title}
              </button>
            )}
          </React.Fragment>
        ))}
      </div>
    );
  }

  if (itemToShow) {
    return (
      <div className={styles.settings}>
        <div className={styles.header}>
          <div className={styles.back} onClick={() => setItemToShow(null)}>
            <BackIcon />
            <h2>Back</h2>
          </div>
          <p className={styles.heading}>{itemToShow?.title}</p>
        </div>
        <div>
          {itemToShow?.information?.map((item, ind) => (
            <div key={ind}>
              <p className={styles.grpHeading}>{item.title}</p>
              <div className={styles.infoContainer}>
                {item.items.map((section, ind, arr) => (
                  <div key={ind}>
                    <DetailRow name={section?.key} text={section?.value} noBorder={ind === arr.length - 1} />
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={styles.settings}>
      {/* TODO: this should never be true due to the condition above if (itemToShow) return... */}
      {/* (this is temporary so I can focus on generators)  */
      /* eslint-disable-next-line no-nested-ternary */}
      {itemToShow ? (
        <div>
          <div className={styles.header}>
            <div className={styles.back} onClick={() => setItemToShow(null)}>
              <BackIcon />
              <h2>Back</h2>
            </div>
            <p className={styles.heading}>Details</p>
          </div>
          <div>
            {itemToShow.sections.map((item, ind) => (
              <div key={ind}>
                <p className={styles.grpHeading}>{item.title}</p>
                <div className={styles.infoContainer}>
                  {item.items.map((section, sind, arr) => (
                    <div key={sind}>
                      <DetailRow name={section.key} text={section.value} noBorder={ind === arr.length - 1} />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : unitDetailShow ? (
        <div>
          <div className={styles.header}>
            <div className={styles.back} onClick={() => setUnitDetailShow(false)}>
              <BackIcon />
              <h2>Back</h2>
            </div>
            <p className={styles.heading}>Wind Sensor</p>
          </div>
          <div className={styles.infoContainer} style={{ marginTop: "20px" }}>
            <DetailRow name="Wind Sensor" toggle />
          </div>
          <p className={styles.windSensorSubText}>The awning will auto-retract when there is inclement weather.</p>
          <div className={styles.sensitivityContainer}>
            <p className={styles.windSensorSubTextB}>SENSITIVITY</p>
            <div className={styles.controllerBox}>
              <SensitivityController />
            </div>
            <p className={styles.windSensorSubText}>
              Sensitivity 3: Medium Winds can trigger the awning to auto-retract.
            </p>
          </div>

          <button type="button" className={styles.restoreBtn}>
            Restore Default
          </button>
        </div>
      ) : (
        <div className={styles.max}>
          <div className={styles.header}>
            <Close onClick={handleClose} className={styles.closeIcon} />
            <p className={styles.heading}>Awning Settings</p>
          </div>

          {settingsData?.data?.map((item, ind) => (
            <React.Fragment key={ind}>
              {item?.type === "LIST_ITEM_NAV" && (
                <div
                  onClick={() => setWindSensorSetting(item)}
                  className={styles.infoContainer}
                  style={{ marginTop: "20px" }}
                >
                  <DetailRow name={item?.title} text={item?.value} arrow noBorder />
                </div>
              )}
              {item?.type === "LIST_ITEM" && (
                <>
                  <p className={styles.infoText}>{item?.title}</p>
                  <div className={styles.infoContainer}>
                    {item?.data?.map((subdata, sindex) => (
                      <div key={sindex} onClick={() => setItemToShow(subdata?.data?.[0])}>
                        <DetailRow name={subdata?.title} arrow noBorder />
                      </div>
                    ))}
                  </div>
                </>
              )}
              {item?.type === "SECTIONS_LIST" && (
                <>
                  <p className={styles.infoText}>{item?.title}</p>
                  <div className={styles.infoContainer}>
                    {item?.data?.map((subdata, sindex) => (
                      <div key={sindex} onClick={() => setDisclaimer(subdata?.data?.[0])}>
                        <DetailRow name={subdata?.title} arrow noBorder />
                      </div>
                    ))}
                  </div>
                </>
              )}
            </React.Fragment>
          ))}
        </div>
      )}
    </div>
  );
}

export default AwningSettings;
