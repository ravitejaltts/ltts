import { useNavigate } from "react-router-dom";
import { BackIcon, SettingsIcon } from "../../assets/asset";

export default function WaterHeading({ settings, title }) {
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
