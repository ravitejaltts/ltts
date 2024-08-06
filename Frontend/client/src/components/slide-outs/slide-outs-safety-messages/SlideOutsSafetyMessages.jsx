import React from "react";
import { useNavigate } from "react-router-dom";
import styles from "./safety.module.css";
import { Close } from "../../../assets/asset";
import { SlideOutWarning, WarningIcon } from "../../../assets/assets";
import { useFetch } from "../../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../../utils/api";

const SlideOutsSafetyMessages = ({ successCb, simple, simpleCb, fetchString }) => {
  const { data } = useFetch(API_ENDPOINT?.[fetchString], LOCAL_ENDPOINT?.[fetchString], false, 10000);

  const navigate = useNavigate();

  const close = () => {
    if (simple) {
      simpleCb();
    } else {
      navigate(-1);
    }
  };

  console.log("data!!", data);
  return (
    <div className={styles.awningSafetyMessages}>
      <div className={styles.topCross} onClick={close}>
        <Close />
      </div>
      <div className={`${styles.contentContainer} custom-scrollbar`}>
        <h2 className={styles.slideOutHeading}>{data?.title}</h2>
        <div className={`${styles.textContainer} custom-scrollbar`}>
          {data?.data?.slice(0, -1)?.map((messages, ind) => (
            <React.Fragment key={ind}>
              <div className={styles.cautionText}>
                {messages?.title == "Caution" && <WarningIcon />}
                {(messages?.title == "Warning" || messages?.title == "Danger") && <SlideOutWarning />}
                <p>{messages?.title}</p>
              </div>
              <p className={styles.description}>{messages?.body}</p>
            </React.Fragment>
          ))}
        </div>

        {!simple && data?.data?.slice(-1)[0] && (
          <div className={styles.bottomContent}>
            <button onClick={successCb}>{data?.data?.slice(-1)[0]?.title}</button>
            <p className={styles.bottomText}>{data?.data?.slice(-1)[0]?.subtext}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SlideOutsSafetyMessages;
