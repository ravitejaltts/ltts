import React, { useContext } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { BackIcon } from "../../../../assets/asset";
import SettingRow from "../../../lighting/SettingRow";
import styles from "./display.module.css";
import BrightnessSlider from "./slider/BrightnessSlider";
import lightSrc from "../../../../assets/images/settings/LightMode.png";
import darkSrc from "../../../../assets/images/settings/DarkMode.png";
import { AppContext } from "../../../../context/AppContext";
import { DARK_MODE, LIGHT_MODE } from "../../../constants/CONST";

const DisplaySettings = ({ data }) => {
  const navigate = useNavigate();
  const { theme, toggleTheme } = useContext(AppContext);

  const changeTheme = (value) => {
    toggleTheme(value);
  };

  const callDimAfter = (href, value) => {
    axios.put(href, {
      value,
    });
  };

  function typeSelector(selected, isLast) {
    if (selected?.type === "SimpleSlider") {
      return <BrightnessSlider data={selected} />;
    }
    if (selected?.type === "ToggleButton") {
      return (
        <div className={styles.row}>
          <div>{selected?.title}</div>
          <div className={styles.selectContainerFan}>
            {selected?.ToggleButton?.options.map((item, ind, arr) => (
              <div
                className={`${styles.selectOptions} ${item.selected && styles.activeBtn}
              ${ind !== arr.length - 1 && styles.rightDivider}
              `}
                key={item.key}
                value={item.value}
                onClick={() => {
                  callDimAfter(selected?.action_default?.action?.href, item.value);
                }}
              >
                {item?.key}
              </div>
            ))}
          </div>
        </div>
      );
    }
    if (selected?.type === "CustomSelect") {
      return (
        <div className={styles.appearanceContainer}>
          <div
            className={`${styles.imgBox} ${theme === LIGHT_MODE && styles.selectedTheme}`}
            onClick={() => changeTheme(LIGHT_MODE)}
          >
            <img src={lightSrc} alt="light mode" />
          </div>
          <div
            className={`${styles.imgBox} ${theme === DARK_MODE && styles.selectedTheme}`}
            onClick={() => changeTheme(DARK_MODE)}
          >
            <img src={darkSrc} alt="dark mode" />
          </div>
        </div>
      );
    }
    return (
      <SettingRow
        name={selected?.title}
        text={selected?.value}
        noBorder={isLast}
      />
    );
  }

  console.log("ss data", data);

  return (
    <div className={styles.displaySettings}>
      <div className={styles.header}>
        <div className={styles.back} onClick={() => navigate(-1)}>
          <BackIcon />
          <h2>Back</h2>
        </div>
        <p className={styles.heading}>{data?.title}</p>
      </div>
      {data?.data?.map((item, ind) => (
        <React.Fragment key={ind}>
          <p className={styles.containerTopText}>{item?.title}</p>
          <div className={styles.container}>
            {item?.data?.map((dat, i) => (
              <React.Fragment key={i}>
                {typeSelector(dat, (item?.data?.length || 0) - 1 === i)}
              </React.Fragment>
            ))}
          </div>
        </React.Fragment>
      ))}
      {/* <p className={styles.containerTopText}>Brightness</p>
      <div className={styles.container}>
        <BrightnessSlider data={data?.data[0]?.data[0]?.SimpleSlider} />

        <div className={`flex justify justify-between ${styles.dimContainer}`}>
          <p>Dim display after</p>
          <select>
            {data?.data[0]?.data[1]?.ToggleButton?.options?.map((item, ind) => (
              <option key={ind} selected={item?.selected}>
                {item?.key}
              </option>
            ))}
          </select>
        </div>
      </div>

      <p className={styles.containerTopText}>Sleep</p>
      <div className={styles.container}>
        <SettingRow name="Slide Show" toggle />

        <div className={`flex justify justify-between ${styles.dimContainer}`}>
          <p>Slideshow begins after</p>
          <select>
            <option>5 mins</option>
            <option>4 mins</option>
            <option>3 mins</option>
          </select>
        </div>
        <SettingRow name="Turn off atr" text="Sunset" />
      </div>

      <p className={styles.containerTopText}>Appearance</p>
      <div className={styles.appearanceContainer}>
        <div
          className={`${styles.imgBox} ${
            theme === LIGHT_MODE && styles.selectedTheme
          }`}
          onClick={() => changeTheme(LIGHT_MODE)}
        >
          <img src={lightSrc} alt="light mode" />
        </div>
        <div
          className={`${styles.imgBox} ${
            theme === DARK_MODE && styles.selectedTheme
          }`}
          onClick={() => changeTheme(DARK_MODE)}
        >
          <img src={darkSrc} alt="dark mode" />
        </div>
      </div> */}
    </div>
  );
};

export default DisplaySettings;
