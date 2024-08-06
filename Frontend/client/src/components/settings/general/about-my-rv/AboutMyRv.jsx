import React from "react";
import { useNavigate } from "react-router-dom";
import { BackIcon } from "../../../../assets/asset";
import SettingRow from "../../../../components/lighting/SettingRow";
import styles from "./about.module.css";

const AboutMyRv = ({ data }) => {
  const navigate = useNavigate();
  return (
    <div className={styles.aboutRvContainer}>
      <div className={styles.header}>
        <div className={styles.back} onClick={() => navigate(-1)}>
          <BackIcon />
          <h2>Back</h2>
        </div>
        <p className={styles.heading}>{data.title}</p>
      </div>
      {data?.data?.map((item, ind) => (
        <React.Fragment key={ind}>
          <p className={styles.containerTopText}>{item.title}</p>
          <div className={styles.container}>
            {item?.data?.map((dat, ind, arr) => (
              <React.Fragment key={ind}>
                <SettingRow
                  name={dat?.title}
                  text={dat?.value?.version || dat?.value}
                  bottomText={dat?.subtext}
                  noBorder={ind === arr.length - 1}
                />
              </React.Fragment>
            ))}
          </div>
        </React.Fragment>
      ))}
    </div>
  );
};

export default AboutMyRv;
