import { useState } from "react";
import { BackIcon, Close, TrumaLogo } from "../../../assets/asset";

import { useFetch } from "../../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../../utils/api";
import SettingRow from "../../settings/setting-row/SettingRow";
import ConfigDetails from "./ConfigDetails/ConfigDetails";
import styles from "./water.module.css";

function WaterSettings({ handleClose }) {
  const { data, refreshDataImmediate } = useFetch(
    API_ENDPOINT.WATER_SYSTEM_SETTING,
    LOCAL_ENDPOINT.WATER_SYSTEM_SETTING,
    false,
  );

  const dataConfiguration = data?.configuration;
  const [itemToShow, setItemToShow] = useState(null);
  const [configDetailIndex, setConfigDetailIndex] = useState(-1);
  let configDetail = null;

  if (configDetailIndex > -1 && dataConfiguration && dataConfiguration.length > configDetailIndex) {
    configDetail = dataConfiguration[configDetailIndex];
    configDetail.type = "WATER_TEMPERATURE";
  }

  return (
    <div className={styles.settings}>
      {itemToShow && (
        <div>
          <div className={styles.header}>
            <div className={styles.back} onClick={handleClose}>
              <BackIcon />
              <h2 className={styles.backText}>Back</h2>
            </div>
            <p className={styles.heading}>Details</p>
          </div>
          <div>
            {itemToShow.sections.map((item, ind) => (
              <div key={ind}>
                <p className={styles.grpHeading}>{item.title}</p>
                <div className={styles.infoContainer}>
                  {item.items
                    .filter((setting) => setting.type !== "LOGO")
                    .map((section, ind, arr) => (
                      <div key={ind}>
                        <SettingRow name={section.key} text={section.value} noBorder={ind === arr.length - 1} />
                      </div>
                    ))}
                </div>
                {item.items
                  .filter((setting) => setting.type === "LOGO")
                  .map(
                    (section, ind) =>
                      section.value === "Truma" && (
                        <div className={styles.centerLogo} key={ind}>
                          <TrumaLogo />
                        </div>
                      ),
                  )}
              </div>
            ))}
          </div>
        </div>
      )}
      {!itemToShow &&
        (configDetail ? (
          <ConfigDetails
            config={configDetail}
            setConfigDetailIndex={setConfigDetailIndex}
            refreshDataImmediate={refreshDataImmediate}
          />
        ) : (
          <div className={styles.max}>
            <div className={styles.header}>
              <Close onClick={handleClose} className={styles.closeIcon} />
              <p className={styles.heading}>Water Systems Settings</p>
            </div>

            {dataConfiguration?.length &&
              dataConfiguration?.map((config, index) => (
                <>
                  <p className={styles.infoTextWater}>{config?.title}</p>
                  <div
                    onClick={() => setConfigDetailIndex(index)}
                    className={styles.infoContainer}
                    style={{ marginTop: "10px" }}
                  >
                    <SettingRow name={config?.items[0]?.title} text={config?.items[0]?.selected_text} arrow noBorder />
                  </div>
                </>
              ))}
            {/* <div className={styles.trumaLogo}>
            <TrumaLogo />
          </div> */}
            <p className={styles.infoText}>{data?.information?.length && data?.information[0]?.title}</p>
            <div className={styles.infoContainer}>
              {data?.information?.length &&
                data?.information[0]?.items?.map((item, ind, arr) => (
                  <div key={ind} onClick={() => setItemToShow(item)}>
                    <SettingRow name={item.title} arrow noBorder={ind === arr.length - 1} />
                  </div>
                ))}
            </div>
          </div>
        ))}
    </div>
  );
}

export default WaterSettings;
