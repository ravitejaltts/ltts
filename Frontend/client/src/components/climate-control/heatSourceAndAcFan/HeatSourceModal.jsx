import axios from "axios";
import { Close } from "../../../assets/asset";
import styles from "./heatFan.module.css";

const HeatSourceModal = ({ changeModal, heatData, refreshDataImmediate }) => {
  const btnAction = (value) => {
    axios
      .put(heatData?.ToggleModal?.action_default?.action?.href, {
        sourceMode: value,
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
        <h2>{heatData?.text}</h2>
        <p>Select a heat source for your heater</p>
        <div className={styles.btnContainer}>
          {heatData?.ToggleModal?.options.map((option) => {
            return (
              <div
                key={option?.key}
                className={`${styles.btn} ${
                  option?.selected ? styles.activeBtn : ""
                }`}
                onClick={() => btnAction(option?.value)}
              >
                {option?.key}
              </div>
            );
          })}
        </div>
        <div className={styles.bottomTexts}>
          <div className={styles.bottomText}>
            <p
              className={styles.greenDot}
              style={{ backgroundColor: heatData?.ToggleModal?.footerColor1 }}
            ></p>
            <p className={styles.txt}>{heatData?.ToggleModal?.footerText1}</p>
          </div>
          <div className={styles.bottomText}>
            <p
              className={styles.greenDot}
              style={{ backgroundColor: heatData?.ToggleModal?.footerColor2 }}
            ></p>
            <p className={styles.txt}>{heatData?.ToggleModal?.footerText2}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HeatSourceModal;
