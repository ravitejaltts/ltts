import { useNavigate } from "react-router-dom";
import { BackIcon } from "../../../../assets/asset";
import DetailRow from "../../../common/detail-row/DetailRow";
import styles from "./index.module.css";

const UnitPreferences = ({ data }) => {
  const navigate = useNavigate();
  return (
    <div className={styles.mainContainer}>
      <div className={styles.header}>
        <div className={styles.back} onClick={() => navigate(-1)}>
          <BackIcon />
          <h2>Back</h2>
        </div>
        <p className={styles.heading}>{data?.title}</p>
      </div>
      <div className={styles.contentContainer}>
        <p className={styles.containerTopText}>TEMPERATURE</p>
        <div className={styles.container}>
          <DetailRow name="Fahrenheit" selected />
          <DetailRow name="Celsius" />
        </div>
        <p className={styles.containerTopText}>DISTANCE</p>
        <div className={styles.container}>
          <DetailRow name="Miles" selected />
          <DetailRow name="Kilometers" />
        </div>
        <p className={styles.containerTopText}>VOLUME</p>
        <div className={styles.container}>
          <DetailRow name="Gallons" selected />
          <DetailRow name="Liters" />
        </div>
      </div>
    </div>
  );
};

export default UnitPreferences;
