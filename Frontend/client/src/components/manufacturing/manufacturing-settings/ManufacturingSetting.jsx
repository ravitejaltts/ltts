import axios from "axios";
import React, { useState } from "react";

import styles from "./manufac.module.css";
import { useFetch } from "../../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../../utils/api";
import { BackIcon, Close } from "../../../assets/asset";
import SettingRow from "../../settings/setting-row/SettingRow";

const ManufacturingSettings = ({ handleClose }) => {
  const { data, refreshDataImmediate } = useFetch(
    API_ENDPOINT.MANUFACTURING_SETTINGS,
    LOCAL_ENDPOINT.MANUFACTURING_SETTINGS,
    false
  );
  const [itemToShow, setItemToShow] = useState(null);
  const [unitDetailShow, setUnitDetailShow] = useState(false);

  const changeUnit = (value) => {
    axios
      .put(data?.configuration[0].items[0].action_default?.action?.href, {
        value: value,
        item: "VolumeUnitPreference",
      })
      .then((res) => {
        refreshDataImmediate();
      })
      .catch((err) => console.error(err));
  };

  return (
    <div className={styles.settings}>
      {itemToShow ? (
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
                      <SettingRow
                        name={section.key}
                        text={section.value}
                        noBorder={ind === arr.length - 1}
                      />
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
            <div
              className={styles.back}
              onClick={() => setUnitDetailShow(false)}
            >
              <BackIcon />
              <h2>Back</h2>
            </div>
            <p className={styles.heading}>Unit Preferences</p>
          </div>
          <div className={styles.infoContainer} style={{ marginTop: "20px" }}>
            {data?.configuration[0]?.items[0]?.options?.map(
              (option, ind, arr) => (
                <div key={ind} onClick={() => changeUnit(option.value)}>
                  <SettingRow
                    name={option.key}
                    selected={option.selected}
                    value={option.value}
                    noBorder={ind === arr.length - 1}
                  />
                </div>
              )
            )}
          </div>
        </div>
      ) : (
        <div className={styles.max}>
          <div className={styles.header}>
            <Close onClick={handleClose} className={styles.closeIcon} />
            <p className={styles.heading}>Manufacturing Settings</p>
          </div>
          {data?.configuration?.length && (
            <div
              onClick={() => setUnitDetailShow(true)}
              className={styles.infoContainer}
              style={{ marginTop: "40px" }}
            >
              <SettingRow
                name={data?.configuration[0]?.items[0]?.title}
                text={data?.configuration[0]?.items[0]?.selected_text}
                arrow
                noBorder
              />
            </div>
          )}
          {/* <p className={styles.infoText}>MANUFACTURER INFORMATION</p> */}
          <div className={styles.infoContainer}>
            {data?.information?.length &&
              data?.information[0]?.items?.map((item, ind, arr) => (
                <div key={ind} onClick={() => setItemToShow(item)}>
                  <SettingRow
                    name={item.title}
                    arrow
                    noBorder={ind === arr.length - 1}
                  />
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ManufacturingSettings;
