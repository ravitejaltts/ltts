import React from "react";
import { useNavigate } from "react-router-dom";
import { BackIcon, SettingsIcon } from "../../assets/asset";

// If this is used by more than two screens, then refactor as a general component.
function LightingHeading({ settings, title }) {
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
        <div className="settingsContainer" onClick={() => settings()}>
          <SettingsIcon />
        </div>
      </div>
      <h2 className="headingText">
        {title?.split(" ")?.map((word, ind) => (
          <p className="m-0" key={ind}>
            {word}
          </p>
        ))}
      </h2>
    </>
  );
}

export default LightingHeading;
