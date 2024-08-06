import axios from "axios";
import React, { useEffect, useState } from "react";
import { BackIcon, Close } from "../../../assets/asset";
import SettingRow from "../../../components/lighting/SettingRow";
import { useFetch } from "../../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../../utils/api";
import { getDataFromLocal, setDataToLocal } from "../../constants/helper";
import styles from "./inverter.module.css";

const InverterSettings = ({ handleClose }) => {
  const { data, refreshDataImmediate } = useFetch(
    API_ENDPOINT.INVERTER_SETTING,
    LOCAL_ENDPOINT.INVERTER_SETTING,
    false
  );
  const [itemToShow, setItemToShow] = useState(null);

  return (
    <div className={styles.settings}>
      {itemToShow ? (
        <div>
          <div className={styles.header}>
            <div className={styles.back} onClick={() => setItemToShow(null)}>
              <BackIcon />
              <h2>Back</h2>
            </div>
            <p className={styles.heading}>Inverter</p>
          </div>
          <div>
            <div>
              <p className={styles.grpHeading}></p>
              <div className={styles.infoContainer}>
                {itemToShow?.sections[0]?.items?.map((section, i, arr) => (
                  <div key={i}>
                    <SettingRow
                      name={section?.key}
                      text={section?.value}
                      noBorder={i === arr.length - 1}
                    />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className={styles.max}>
          <div className={styles.header}>
            <Close onClick={handleClose} className={styles.closeIcon} />
            <p className={styles.heading}>{data?.title}</p>
          </div>

          <p className={styles.infoText}>{data?.information?.title}</p>
          <div className={styles.infoContainer}>
            {data &&
              data?.information[0]?.items?.map((info, i, arr) => (
                <div key={i} onClick={() => setItemToShow(info)}>
                  <SettingRow
                    name={info?.title}
                    arrow
                    noBorder={i === arr.length - 1}
                  />
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default InverterSettings;
