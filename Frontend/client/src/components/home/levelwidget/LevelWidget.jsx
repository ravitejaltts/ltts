import React from "react";
import { useNavigate } from "react-router-dom";
import styles from "./level.module.css";

const LevelWidget = (props) => {

  const { data, cls, height, width, reRoute } = props;
  const navigate = useNavigate();

  const redirect = () => {
    if (reRoute) {
      navigate(data?.action_default?.action?.href);
    }
  };

  return (
    <div className={styles.system} style={{ height, width }} onClick={redirect}>
      <div
        className={styles.top}
        style={{ backgroundColor: data?.color_empty }}
      >
        <div className={styles.icon}>{props.icon}</div>
        <div className={styles.levelText}>{data?.state?.level_text}</div>
        <div
          className={`${styles.colorFill} ${cls}`}
          style={{
            height: `${data?.state?.current_value}%`
          }}
        ></div>
      </div>
      <div className={styles.bottom}>
        <div className={styles.title}>
          {data?.title?.split(" ")?.map((word, ind) => (
            <p className="m-0" key={ind}>
              {word}
            </p>
          ))}
        </div>
        <p className={styles.subText}>{data?.subtext}</p>
      </div>
    </div>
  );
};

export default LevelWidget;
