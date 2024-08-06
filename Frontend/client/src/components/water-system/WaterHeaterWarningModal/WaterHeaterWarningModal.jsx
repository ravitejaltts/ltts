import { InfoIconBlue } from "../../../assets/asset";
import styles from "./warning.module.css";

const WaterHeaterWarningModal = ({ toggleInfoModal, information }) => {
  return (
    <div className={styles.warningCont}>
      <div className={styles.topRow}>
        <InfoIconBlue />
        <p>{information?.title}</p>
      </div>

      {information?.items?.map((item) => {
        return (
          <div className={styles.txtCont}>
            <p>
              <b>{item?.title?.split("}")[0]?.substr(1)}</b>{" "}
              {item?.title?.split("}")[1]}
            </p>
            {item?.items?.map((bulletPoint) => (
              <div className={styles.txtWithDot}>
                <span className={styles.dot}></span>
                <p>{bulletPoint}</p>
              </div>
            ))}
          </div>
        );
      })}

      {/* <div className={styles.txtCont}>
        <p>
          <b>Eco Mode</b> saves energy and prevents freezing
        </p>
        <div className={styles.txtWithDot}>
          <span className={styles.dot}></span>
          <p>
            The temperature in the appliance is automatically kept above 41 c
          </p>
        </div>
      </div>

      <div className={styles.txtCont}>
        <p>
          <b>Comfort Mode</b> maintains stand-by heat for rapid availability of
          hot water.
        </p>
        <div className={styles.txtWithDot}>
          <span className={styles.dot}></span>
          <p>
            The temperature in the appliance is automatically kept above 102 c
          </p>
        </div>
      </div> */}

      <p className={styles.close} onClick={toggleInfoModal}>
        Close
      </p>
    </div>
  );
};

export default WaterHeaterWarningModal;
