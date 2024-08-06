import axios from "axios";
import React, { useState } from "react";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../../utils/api";
import { BackIcon, Close } from "../../../assets/asset";
import SettingRow from "../../../components/lighting/SettingRow";
import { useFetch } from "../../../hooks/useFetch";
import styles from "./settings.module.css";

function GeneratorSettings({ handleClose }) {
  const { data, refreshDataImmediate } = useFetch(
    API_ENDPOINT.GENERATOR_SETTING,
    LOCAL_ENDPOINT.GENERATOR_SETTING,
    false,
  );
  const [itemToShow, setItemToShow] = useState(null);
  const [unitDetailShow, setUnitDetailShow] = useState(false);

  const changeUnit = (value) => {
    axios
      .put(data?.configuration[0].items[0].action_default?.action?.href, {
        value,
        item: "VolumeUnitPreference",
      })
      .then(() => {
        refreshDataImmediate();
      })
      .catch((err) => console.error(err));
  };

  return (
    <div className={styles.settings}>
      {itemToShow && (
        <div>
          <div className={styles.header}>
            <div className={styles.back} onClick={() => setItemToShow(null)}>
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
      )}
      {!itemToShow && unitDetailShow && (
        <div>
          <div className={styles.header}>
            <div className={styles.back} onClick={() => setUnitDetailShow(false)}>
              <BackIcon />
              <h2 className={styles.backTxt}>Back</h2>
            </div>
            <p className={styles.heading}>Unit Preferences</p>
          </div>
          <div className={styles.infoContainer} style={{ marginTop: "20px" }}>
            {data?.configuration[0]?.items[0]?.options?.map((option, ind, arr) => (
              <div key={ind} onClick={() => changeUnit(option.value)}>
                <SettingRow
                  name={option.key}
                  selected={option.selected}
                  value={option.value}
                  noBorder={ind === arr.length - 1}
                />
              </div>
            ))}
          </div>
        </div>
      )}
      {!itemToShow && !unitDetailShow && (
        <div className={styles.max}>
          <div className={styles.header}>
            <Close onClick={handleClose} className={styles.closeIcon} />
            <p className={styles.heading}>{data?.title}</p>
          </div>
          {data?.configuration?.length && (
            <div onClick={() => setUnitDetailShow(true)} className={styles.infoContainer} style={{ marginTop: "40px" }}>
              <SettingRow
                name={data?.configuration[0]?.items[0]?.title}
                text={data?.configuration[0]?.items[0]?.selected_text}
                arrow
                noBorder
              />
            </div>
          )}
          <p className={styles.infoText}>{data?.information[0]?.title}</p>
          <div className={styles.infoContainer}>
            {data?.information?.length &&
              data?.information[0]?.items?.map((item, ind, arr) => (
                <div key={ind} onClick={() => setItemToShow(item)}>
                  <SettingRow name={item.title} arrow noBorder={ind === arr.length - 1} />
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default GeneratorSettings;
