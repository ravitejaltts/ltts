import { useState } from "react";
import { useFetch } from "../../hooks/useFetch";
import axios from "axios";
import { BackIcon, Close } from "../../assets/asset";
import SettingRow from "../../components/lighting/SettingRow";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../utils/api";
import styles from "./climate.module.css";

const ClimateSettings = ({ handleClose }) => {
  const { data: settingsData, refreshDataImmediate: toggleRefresh } = useFetch(
    API_ENDPOINT.CLIMATE_CONTROL_SETTING,
    LOCAL_ENDPOINT.CLIMATE_CONTROL_SETTING,
    false,
  );
  const [itemToShow, setItemToShow] = useState(null);
  const [unitDetailShow, setUnitDetailShow] = useState(null);

  const changeUnit = async (value) => {
    await axios
      .put(settingsData?.configuration[0].items[0].action_default?.action?.href, {
        value,
        item: "TempUnitPreference",
      })
      .catch((err) => console.log(err));
    toggleRefresh();
  };
  return (
    <div className={styles.settings}>
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
                  {item.items.map((section, ind, arr) => (
                    <div key={ind}>
                      <SettingRow name={section.key} text={section.value} noBorder={ind === arr.length - 1} />
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
            <p className={styles.heading}>Unit Preferences</p>
          </div>
          <div className={styles.infoContainer} style={{ marginTop: "20px" }}>
            {settingsData?.configuration[0]?.items[0]?.options?.map((option, ind) => (
              <div key={ind} onClick={() => changeUnit(option.value)}>
                <SettingRow name={option.key} selected={option.selected} value={option.value} />
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className={styles.max}>
          <div className={styles.header}>
            <Close onClick={handleClose} className={styles.closeIcon} />
            <p className={styles.heading}>Climate Control Settings</p>
          </div>
          {settingsData?.configuration?.length && (
            <div onClick={() => setUnitDetailShow(true)} className={styles.infoContainer} style={{ marginTop: "20px" }}>
              <SettingRow
                name={settingsData?.configuration[0]?.items[0]?.title}
                text={settingsData?.configuration[0]?.items[0]?.selected_text}
                arrow
                noBorder={true}
              />
            </div>
          )}
          <p className={styles.infoText}>Manufacturer Information</p>
          <div className={styles.infoContainer}>
            {settingsData?.information?.length &&
              settingsData?.information[0]?.items?.map((item, ind, arr) => (
                <div key={ind} onClick={() => setItemToShow(item)}>
                  <SettingRow name={item.title} arrow noBorder={ind === arr.length - 1} />
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ClimateSettings;
