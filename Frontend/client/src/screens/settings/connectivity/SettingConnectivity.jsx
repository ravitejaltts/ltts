import axios from "axios";
import React, { useEffect, useState } from "react";
import { useLocation, useOutletContext } from "react-router-dom";
import Button from "../../../components/common/Button/Button";
import BackButton from "../../../components/settings/back-button/BackButton";
import Pairing from "../../../components/settings/pairing/Pairing";
import SettingRow from "../../../components/settings/setting-row/SettingRow";
import { SETTINGS_LINKS } from "../../../constants/CONST";
import styles from "./connectivity.module.css";

const SettingConnectivity = () => {
  const location = useLocation();
  const [setActiveTab, data, refreshDataImmediate] = useOutletContext();
  useEffect(() => {
    setActiveTab(location?.pathname);
  }, []);
  const [selectedRowIndex, setSelectedRowIndex] = useState(-1);
  const [pairingMode, setPairingMode] = useState(false);

  const connectivityData = data?.[0]?.tabs?.find(
    (tab) => `${tab.name}` === SETTINGS_LINKS.CONNECTIVITY
  );
  const connectivityItems =
    connectivityData?.details?.[0]?.data?.[0]?.data?.[0]?.items;

  // This approach is assuming the Pair a device button to be the last item
  const connectivityRowData = connectivityItems.slice(0, -1);
  const pairingData = connectivityItems?.slice(-1)[0];

  let displayInnerDetail = null;

  if (
    selectedRowIndex > -1 &&
    connectivityRowData &&
    connectivityRowData.length > selectedRowIndex
  ) {
    displayInnerDetail = connectivityRowData[selectedRowIndex];
  }

  const renderSupportText = (data) => {
    return <p className={styles.extraText}>{data?.text}</p>;
  };

  function rowRenderer(dat, isLast) {
    console.log(dat);
    if (dat?.type === "Button" || dat?.type === "BUTTON") {
      console.log(dat?.actions);
      return (
        // <button className={styles.pairingButton}>{dat?.title}</button>
        <Button
          // className={styles.actionButton}
          action={dat?.actions?.TAP?.action}
          text={dat?.title}
          refreshParentData={refreshDataImmediate}
        />
      );
    } else if (dat?.type === "CELLULAR_INFO_LABEL") {
      return (
        <SettingRow
          name={dat?.title || dat?.name}
          text={evaluteText(dat)}
          noBorder={isLast}
          bottomText={dat?.subtext?.version}
          // toggle={dat?.actions}
        />
      );
    }
    // else if (dat?.type === "SUPPORT_TEXT") {
    //   return (
    //     <div className={styles.mainRight}>

    //       <React.Fragment>
    //         {renderSupportText(dat)}
    //       </React.Fragment>
    //     </div>
    //   )
    // }
    else {
      return (
        <SettingRow
          name={dat?.title || dat?.name}
          text={evaluteText(dat)}
          noBorder={isLast}
          bottomText={dat?.subtext?.version}
          toggle={dat?.actions}
          toggleState={
            dat?.state?.onoff || dat?.state?.onOff || dat?.value?.onOff || 0
          }
          action={dat?.actions?.TOGGLE?.action || dat?.actions?.DISPLAY?.action}
        />
      );
    }
  }

  const titleRenderer = (dat) => {
    if (dat?.type === "Button") {
      return (
        <div className="flex justify-center">
          <button
            className={styles.pairingButton}
            onClick={() =>
              dat?.actions?.TAP?.action &&
              handleBtnClick(dat?.actions?.TAP?.action)
            }
          >
            {pairingData?.title}
          </button>
        </div>
      );
    } else {
      return <p className={styles.containerHeading}>{dat?.title}</p>;
    }
  };

  const handleBtnClick = (action) => {
    axios.put(action?.href, {
      onOff: 1,
    });
  };

  const togglePairingMode = () => {
    setPairingMode((p) => !p);
  };

  const evaluteText = (data) => {
    if ("connected" in data) {
      return data.connect ? "Connected" : "Not Connected";
    }
    const value = data?.value;
    if (typeof value === "string") {
      return value;
    }
    if (typeof value === "object") {
      if ("version" in value && typeof value?.version === "string") {
        return value?.version;
      }
      if ("status" in value && typeof value?.status === "string") {
        return value?.status;
      }
    } else {
      return "";
    }
  };

  if (pairingMode) {
    return <Pairing close={togglePairingMode} data={pairingData?.data?.[0]} />;
  }

  return (
    <>
      {displayInnerDetail ? (
        <div>
          <div className={styles.header}>
            <div className={styles.backBtn}>
              <BackButton handler={() => setSelectedRowIndex(-1)} />
            </div>
            <p className={styles.headingText}>{displayInnerDetail?.title}</p>
          </div>
          {displayInnerDetail?.data?.[0]?.data?.map((item, ind) => (
            <React.Fragment key={ind}>
              <div className={styles.itemContainer}>
                {titleRenderer(item)}
                <div className={styles.contentContainer}>
                  {item?.data?.filter(dat => dat.type != 'SUPPORT_TEXT').map((dat, ind, arr) => (
                    <React.Fragment key={ind}>
                      {rowRenderer(dat, ind === arr.length - 1)}
                    </React.Fragment>
                  ))}
                </div>
                <div>
                  {item?.data?.filter(dat => dat.type === 'SUPPORT_TEXT').map((dat, ind, arr) => (
                      <React.Fragment key={ind}>
                        {renderSupportText(dat, ind === arr.length - 1)}
                      </React.Fragment>
                  ))}
                </div>
              </div>
            </React.Fragment>
          ))}
        </div>
      ) : connectivityData ? (
        <>
          <div className={styles.header}>
            <p className={styles.headingText}>{connectivityData?.title}</p>
          </div>
          <div className={styles.itemContainer}>
            <p className={styles.containerHeading}>{connectivityData?.title}</p>
            <div className={styles.contentContainer}>
              {connectivityRowData?.map((dat, index, arr) => (
                <div key={index} onClick={() => setSelectedRowIndex(index)}>
                  <SettingRow
                    refreshDataImmediate={refreshDataImmediate}
                    name={dat?.title}
                    text={dat?.value}
                    noBorder={index === arr.length - 1}
                    arrow
                  />
                </div>
              ))}
            </div>
            <div className={styles.pairingContainer}>
              {pairingData && (
                <button
                  className={styles.pairingButton}
                  onClick={togglePairingMode}
                >
                  {pairingData?.title}
                </button>
              )}
            </div>
          </div>
        </>
      ) : null}
    </>
  );
};

export default SettingConnectivity;
