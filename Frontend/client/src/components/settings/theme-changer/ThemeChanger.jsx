import React, { useContext } from "react";
import axios from "axios";
import { AppContext } from "../../../context/AppContext";
import { DARK_MODE, LIGHT_MODE } from "../../constants/CONST";
import styles from "./theme.module.css";
import lightSrc from "../../../assets/images/settings/LightMode.png";
import darkSrc from "../../../assets/images/settings/DarkMode.png";
import { Tick } from "../../../assets/asset";

function ThemeChanger({ data }) {
  const { theme, toggleTheme } = useContext(AppContext);
  const changeTheme = (value) => {
    toggleTheme(value);
    axios.put(data.actions.TAP.href, { value });
  };
  return (
    <div className={styles.appearanceContainer}>
      <div
        className={`${styles.imgBox} ${
          theme === LIGHT_MODE && styles.selectedTheme
        }`}
        onClick={() => changeTheme(LIGHT_MODE)}
      >
        <img src={lightSrc} alt="light mode" />
        <p className={styles.themeText}>Light Mode</p>
        {theme === LIGHT_MODE ? (
          <div className={styles.checkbox}>
            <Tick />
          </div>
        ) : (
          <div className={styles.uncheckbox} />
        )}
      </div>
      <div
        className={`${styles.imgBox} ${
          theme === DARK_MODE && styles.selectedTheme
        }`}
        onClick={() => changeTheme(DARK_MODE)}
      >
        <img src={darkSrc} alt="dark mode" />
        <p className={styles.themeText}>Dark Mode</p>
        {theme === DARK_MODE ? (
          <div className={styles.checkbox}>
            <Tick />
          </div>
        ) : (
          <div className={styles.uncheckbox} />
        )}
      </div>
    </div>
  );
}

export default ThemeChanger;
