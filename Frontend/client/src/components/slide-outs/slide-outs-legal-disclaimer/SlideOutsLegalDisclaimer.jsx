import { useNavigate } from "react-router-dom";
import styles from "./slide-outs-legal.module.css";
import { Close } from "../../../assets/asset";

const SlideOutsLegalDisclaimer = ({ data, handleClose }) => {
  console.log("disclaiamer", data);
  const navigate = useNavigate();
  return (
    <div className={styles.legalDisclaimer}>
      <div className={styles.topCross} onClick={handleClose}>
        <Close />
      </div>
      <div className={styles.contentContainer}>
        <h2 className={styles.heading}> {data?.title}</h2>
        <p className={styles.bottomText}>{data?.subtext}</p>
        <p className={styles.description}>{data?.body}</p>
      </div>
    </div>
  );
};

export default SlideOutsLegalDisclaimer;
