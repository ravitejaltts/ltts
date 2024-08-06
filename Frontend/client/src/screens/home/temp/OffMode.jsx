import { useNavigate } from "react-router-dom";
// import { ClimateErrorIcon } from "../../../assets/asset";
import styles from "./off.module.css";

const OffMode = ({ data }) => {
  const navigate = useNavigate();

  const redirect = () => {
    navigate(data?.actions[0]?.action?.href);
  };
  return (
    <div id="com-temp" className={styles.container} onClick={redirect}>
      <div id="com-val" className={styles.mainTemp}>
        <div className={styles.titleText}>Thermostat</div>
        <div className={styles.middleText}>
          {data?.interiorTempText}
          <span className={styles.middleSubText}>{data?.unit}</span>
        </div>

        <div className={styles.endText}>{data?.climateModeSubtext}</div>
      </div>
    </div>
  );
};

export default OffMode;
