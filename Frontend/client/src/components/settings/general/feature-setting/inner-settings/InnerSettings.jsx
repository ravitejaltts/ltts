import { BackIcon } from "../../../../../assets/asset";
import SettingRow from "../../../../lighting/SettingRow";
import styles from "./inner.module.css";

const InnerSettings = ({ setInnerFeatures }) => {
  // const navigate = useNavigate();
  return (
    <div className={styles.aboutRvContainer}>
      <div className={styles.header}>
        <div className={styles.back} onClick={() => setInnerFeatures(false)}>
          <BackIcon />
          <h2>Back</h2>
        </div>
        <p className={styles.heading} style={{ textTransform: "capitalize" }}>
          Light Settings
        </p>
      </div>
      <p className={styles.containerTopText}>Manufacturer Information</p>
      <div className={styles.container}>
        <SettingRow name="Accent" arrow />
        <SettingRow name="Accent" arrow />
        <SettingRow name="Accent" arrow />
        <SettingRow name="Accent" arrow />
        <SettingRow name="Accent" arrow />
        <SettingRow name="Accent" arrow />
      </div>
    </div>
  );
};

export default InnerSettings;
