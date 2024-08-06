import React, { useEffect, useState } from "react";
import { BackIcon, Close } from "../../../assets/asset";
import SettingRow from "../../lighting/SettingRow";
import { useFetch } from "../../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../../utils/api";
import styles from "./slide-out-settings.module.css";

export default function SlideOutsSettings({ handleClose, setShowLegal }) {
  const { data } = useFetch(API_ENDPOINT.SLIDE_OUT_SETTING, LOCAL_ENDPOINT.SLIDE_OUT_SETTING, false, 10000);
  const [displayInnerDetail, setDisplayInnerDetail] = useState(null);

  useEffect(() => {
    if (displayInnerDetail?.title === "Legal Disclaimer") {
      setShowLegal(displayInnerDetail?.data?.[0]);
    }
  }, [displayInnerDetail]);

  return (
    <div className={styles.settings}>
      {!displayInnerDetail && (
        <div className={styles.max}>
          <div className={styles.header}>
            <Close onClick={handleClose} className={styles.closeIcon} />
            <p className={styles.heading}>{data?.title}</p>
          </div>
          {data?.data?.map((item, ind) => (
            <React.Fragment key={ind}>
              <div>
                <p className={styles.containerHeading}>{item.title}</p>
                <div className={styles.contentContainer}>
                  {item?.configuration?.map((dat, ind, arr) => (
                    <div
                      key={ind}
                      onClick={() => {
                        dat?.data && setDisplayInnerDetail(dat);
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
        </div>
      )}
      {displayInnerDetail && (
        <div className={styles.max}>
          <div className={styles.header}>
            <div className={styles.back} onClick={() => setDisplayInnerDetail(null)}>
              <BackIcon />
              <h2>Back</h2>
            </div>
            <p className={styles.heading}>{displayInnerDetail?.title}</p>
          </div>
          {displayInnerDetail?.data?.map((item, ind) => (
            <React.Fragment key={ind}>
              <div>
                <p className={styles.containerHeading}>{item?.title}</p>
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
        </div>
      )}
    </div>
  );
}
