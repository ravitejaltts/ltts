import React, { useState } from "react";
import { BackIcon, Close } from "../../../assets/asset";
import Button from "../../../components/common/Button/Button";
import SettingPopUp from "../../../components/lighting/SettingPopUp";
import SettingRow from "../../../components/lighting/SettingRow";
import { useFetch } from "../../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../../utils/api";
import styles from "./settings.module.css";

function LightingSettings({ setShowModal }) {
  const { data, refreshDataImmediate } = useFetch(
    API_ENDPOINT.LIGHTING_SETTING,
    LOCAL_ENDPOINT.LIGHTING_SETTING,
    false,
  );

  const [showDetails, setShowDetails] = useState(false);

  return (
    <div className={styles.settings}>
      {showDetails ? (
        <div>
          <div className={styles.header}>
            <div className={styles.back} onClick={() => setShowDetails(false)}>
              <BackIcon />
              <span>Back</span>
            </div>
            <p className={styles.heading}>Details</p>
          </div>
          <p className={styles.infoText}>{showDetails?.title}</p>
          <div className={styles.infoContainer}>
            {showDetails?.sections[0]?.items?.map((item, index, arr) => (
              <div key={index}>
                <SettingRow name={item.key} text={item.value} noBorder={index === arr.length - 1} />
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className={styles.max}>
          <div className={styles.header}>
            <Close onClick={() => setShowModal(false)} className={styles.closeIcon} />
            <p className={styles.heading}>Lights Settings</p>
          </div>
          {data?.notifications?.map(() => (
            <SettingPopUp />
          ))}
          <p className={styles.infoText}>{data?.information?.length && data?.information[0]?.title}</p>
          <div className={styles.infoContainer}>
            {data?.information?.length &&
              data?.information[0]?.items?.map((item, ind, arr) => (
                <div key={ind} onClick={() => setShowDetails(item)}>
                  <SettingRow name={item.title} arrow noBorder={ind === arr.length - 1} />
                </div>
              ))}
          </div>
        </div>
      )}
      {data?.bottom && (
        <div>
          {/* container because it future it can have multiple rows. styling need to done in future */}
          <div className={`flex justify-between align-center ${styles.resetRow}`}>
            <p>{data?.bottom?.title}</p>
            <Button action={data?.bottom?.DEFAULT?.action} refreshParentData={refreshDataImmediate} text="Reset" />
          </div>
        </div>
      )}
    </div>
  );
}

export default LightingSettings;
