import axios from "axios";
import { useNavigate } from "react-router-dom";
import SettingRow from "../../lighting/SettingRow";
import styles from "./general.module.css";

const General = ({ data }) => {
  const navigate = useNavigate();
  const navigateTo = (url) => navigate(url);

  const rebootApiCall = async () => {
    axios
      .put("/api/system/reboot")
      .then((res) => {
        // success callback
      })
      .catch((err) => {
        console.error(err);
      });
  };
  return (
    <div className={styles.generalContainer}>
      <h2>{data?.title}</h2>
      {data?.data?.configuration?.map((config, i) => (
        <div key={i} className={styles.container}>
          {config.data.map((configItem, ind, arr) => (
            <div key={ind} onClick={() => navigateTo(configItem.title)}>
              <SettingRow
                name={configItem.title}
                arrow
                noBorder={ind === arr.length - 1}
              />
            </div>
          ))}
        </div>
      ))}
      <button className={styles.resetBtn} onClick={rebootApiCall}>
        Reboot
      </button>
      {/* <div className={styles.container}>
        <div onClick={() => navigateTo("about-my-rv")}>
          <SettingRow name="About My RV" arrow />
        </div>
        <div onClick={() => navigateTo("software-updates")}>
          <SettingRow name="Software Updates" arrow />
        </div>
      </div>
      <div className={styles.container}>
        <div onClick={() => navigateTo("display-settings")}>
          <SettingRow name="Display" arrow />
        </div>
        <div onClick={() => navigateTo("time-and-location")}>
          <SettingRow name="Time and Location" arrow />
        </div>
        <div onClick={() => navigateTo("unit-prefrences")}>
          <SettingRow name="Unit Prefrences" arrow />
        </div>
        <div onClick={() => navigateTo("feature-settings")}>
          <SettingRow name="Feature Settings" arrow />
        </div>
      </div>
      <div className={styles.container}>
        <div onClick={() => navigateTo("data-backup-settings")}>
          <SettingRow name="Data Backup" arrow />
        </div>
        <div onClick={() => navigateTo("wipe-reset-settings")}>
          <SettingRow name="Wipe and Reset WinnConnect" arrow />
        </div>
      </div> */}
    </div>
  );
};

export default General;
