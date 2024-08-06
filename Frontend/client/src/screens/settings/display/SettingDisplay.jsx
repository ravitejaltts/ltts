import React, { useEffect, useState } from "react";
import BackButton from "../../../components/settings/back-button/BackButton";
import BrightnessSlider from "../../../components/settings/brightness-slider/BrightnessSlider";
import SettingRow from "../../../components/settings/setting-row/SettingRow";
import ThemeChanger from "../../../components/settings/theme-changer/ThemeChanger";
import { SETTINGS_LINKS } from "../../../constants/CONST";
import styles from "./display.module.css";
import { useLocation, useOutletContext } from "react-router-dom";

const SettingDisplay = () => {
  const location = useLocation();
  const [setActiveTab, data, refreshDataImmediate] = useOutletContext();
  useEffect(() => {
    setActiveTab(location?.pathname);
  }, []);
  const [displayInnerDetail, setDisplayInnerDetail] = useState(false);

  const brightnessData = data?.[0]?.tabs?.filter(
    (tab) => `${tab.name}` === SETTINGS_LINKS.DISPLAY
  )[0]?.details?.data[0]?.data[0];
  const appearanceData = data?.[0]?.tabs?.filter(
    (tab) => `${tab.name}` === SETTINGS_LINKS.DISPLAY
  )[0]?.details?.data[1];
  const configurationData = brightnessData?.configuration[0]?.data[0];

  function rowRenderer(item, isLast) {
    if (item?.type === "SimpleSlider") {
      return <BrightnessSlider data={item} />;
    }
    if (item?.type === "SIMPLE_ONOFF") {
      return (
        <SettingRow
          name={item?.title}
          // text="test"
          text={item.Simple.onOff ? "On" : "Off"}
          toggle
          noBorder={isLast}
          toggleState={item.Simple.onOff}
          action={item?.actions.TAP.action}
          refreshDataImmediate={refreshDataImmediate}
        />
      );
    }
    if (item?.type === "CustomSelect") {
      return <ThemeChanger data={item} />;
    } else {
      return (
        <SettingRow
          refreshDataImmediate={refreshDataImmediate}
          name={item?.title}
          text={item?.value}
          noBorder={isLast}
        />
      );
    }
  }

  return (
    <>
      <div className={styles.header}>
        {displayInnerDetail && (
          <div className={styles.backBtn}>
            <BackButton handler={() => setDisplayInnerDetail(false)} />
          </div>
        )}
        <p className={styles.headingText}>Display</p>
      </div>
      {displayInnerDetail && (
        <>
          <div className={styles.itemContainer}>
            <p className={styles.containerHeading}>{configurationData.title}</p>
            <div className={styles.contentContainer}>
              {configurationData?.options?.map((dat, ind, arr) => (
                <React.Fragment key={ind}>
                  <SettingRow
                    name={dat?.key}
                    selected={dat?.selected}
                    noBorder={arr.length - 1 === ind}
                    action={configurationData?.actions?.TAP?.action}
                    value={dat.value}
                    refreshDataImmediate={refreshDataImmediate}
                  />
                </React.Fragment>
              ))}
            </div>
          </div>
        </>
      )}
      {!displayInnerDetail && brightnessData && (
        <>
          <div className={styles.itemContainer}>
            <p className={styles.containerHeading}>{brightnessData.title}</p>
            <div className={styles.contentContainer}>
              {brightnessData?.data?.map((dat, ind, arr) => (
                <React.Fragment key={ind}>
                  <React.Fragment>
                    {rowRenderer(dat, arr.length - 1 === ind)}
                  </React.Fragment>
                  {dat?.type === "SimpleSlider" && (
                    <div onClick={() => setDisplayInnerDetail(true)}>
                      <SettingRow
                        name={brightnessData?.configuration[0].data[0].title}
                        arrow
                        noBorder
                      />
                    </div>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>
        </>
      )}
      {!displayInnerDetail && appearanceData && (
        <React.Fragment>
          <div className={styles.itemContainer}>
            <p className={styles.containerHeading}>{appearanceData.title}</p>
            <div className={styles.contentContainer}>
              {appearanceData?.data?.map((dat, ind, arr) => (
                <React.Fragment key={ind}>
                  {rowRenderer(dat, arr.length - 1 === ind)}
                </React.Fragment>
              ))}
            </div>
          </div>
        </React.Fragment>
      )}
    </>
  );
};

export default SettingDisplay;
