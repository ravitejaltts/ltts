import { SettingClose } from "../../../assets/asset";
import AlertIcon from "../AlertIcon";
import styles from "./details.module.css";

const StatusAlertDetails = ({ alert, setStatusAlertDetail }) => {
  const { priority, header, message } = alert;
  return (
    <div className={styles.statusAlertDetails}>
      <SettingClose onClick={() => setStatusAlertDetail(null)} />
      <div className={styles.details}>
        <AlertIcon priority={priority} />
        <h1 className={styles.heading}>{header}</h1>
        <div className="custom-scrollbar">
          <div
            className={`${styles.message} `}
            dangerouslySetInnerHTML={{ __html: message }}
          />
        </div>
      </div>
    </div>
  );
};

export default StatusAlertDetails;
