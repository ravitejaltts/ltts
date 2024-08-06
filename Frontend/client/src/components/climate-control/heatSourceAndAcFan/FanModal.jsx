import axios from "axios";
import { Close } from "../../../assets/asset";
import styles from "./heatFan.module.css";

const FanModal = ({ changeModal, fanData, refreshDataImmediate }) => {
  const btnAction = (value) => {
    axios
      .put(fanData?.ToggleModal?.action_default?.action?.href, {
        fanMode: value,
      })
      .then(() => {
        refreshDataImmediate();
      });
  };
  return (
    <div className={styles.modal}>
      <div className={styles.close}>
        <Close onClick={() => changeModal(null)} />
      </div>
      <div className={styles.modalContent}>
        <h2>{fanData?.text}</h2>
        <p>{fanData?.subtext}</p>
        <div className={styles.btnContainer}>
          {fanData?.ToggleModal?.options.map((option) => {
            console.log("option", option);
            return (
              <div
                key={option?.key}
                className={`${styles.pillToggleButton} ${
                  option?.selected ? styles.pillToggleButtonActive : ""
                }`}
                onClick={() => btnAction(option?.value)}
              >
                {option?.key}
              </div>
            );
          })}
        </div>
        <div className={styles.fanBottomText}>
          {fanData?.footerText}
        </div>
      </div>
    </div>
  );
};

export default FanModal;
