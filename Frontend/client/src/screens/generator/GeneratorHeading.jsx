import React from "react";
import { useNavigate } from "react-router-dom";
import { BackIcon, SettingsIcon } from "../../assets/asset";
import styles from "./generator.module.css";
import screenStyles from "../../style/screen.css";

function GeneratorHeading({ data, settings }) {
  const navigate = useNavigate();

  return (
    <>
      <div className="headerTopControls">
        <div className="backNav" onClick={() => navigate(-1)}>
          <div className="backContainer">
            <BackIcon />
          </div>
          <p className="backText">Back</p>
        </div>
        <div className={styles.settingsContainer} onClick={settings}>
          <SettingsIcon />
        </div>
      </div>
      <h2 className="headingText">
        {data?.overview?.title?.split(" ")?.map((word, ind) => (
          <p className="m-0" key={ind}>
            {word}
          </p>
        ))}
      </h2>
    </>
  );
}

export default GeneratorHeading;
