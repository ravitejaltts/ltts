import React from "react";
import { ClimateErrorIcon } from "../../../assets/asset";
import SettingRow2 from "../setting-row-2/SettingRow2";
import styles from "./row.module.css";
import axios from "axios";

const SettingRow3 = ({
  data,
  noBorder,
  handleMainButtonClick,
  handleButtonClick,
}) => {
  function renderInfo(data) {
    return (
      <>
        {data?.enable ? (
          <>
            <p className={styles.borderBottom} />
            <div className={styles.info}>
              <div className={styles.infoIcon}>
                <ClimateErrorIcon />
              </div>
              <div>{data?.title}</div>
            </div>
          </>
        ) : null}
      </>
    );
  }

  function renderButton(data) {
    return (
      <div className={styles.mainBtnContainer}>
        <button
          disabled={!data?.enable}
          onClick={() => handleMainButtonClick(data)}
          className={`${styles.mainBtn} ${!data?.enable && styles.disableBtn}`}
        >
          {data?.title}
        </button>
      </div>
    );
  }

  return (
    <>
      {data?.map((rowData, ind, arr) => (
        <React.Fragment key={ind}>
          {rowData?.type === "MULTI_NAVIGATION_BUTTON" && (
            <SettingRow2
              name={rowData?.title}
              bottomText={rowData?.subtitle}
              buttonData={rowData?.button}
              handleButtonClick={handleButtonClick}
              noBorder
            />
          )}
          {rowData?.type === "PURE_INFO" && renderInfo(rowData)}
          {rowData?.type === "BUTTON" && renderButton(rowData)}
        </React.Fragment>
      ))}
      {!noBorder && <p className={styles.borderBottom}></p>}
    </>
  );
};

export default SettingRow3;
