import { Close } from "../../../assets/asset";
import styles from "./legal.module.css";

function AwningLegalDisclaimer({ data, closeCb }) {
  return (
    <div className={styles.legalDisclaimer}>
      <div className={styles.topCross} onClick={closeCb}>
        <Close />
      </div>
      <div className={`${styles.contentContainer} custom-scrollbar`}>
        <h2 className={styles.title}>{data?.title}</h2>
        <p className={styles.bottomText}>{data?.subtext}</p>
        <p className={` ${styles.description} `}>{data?.body}</p>
      </div>
    </div>
  );
}

export default AwningLegalDisclaimer;
