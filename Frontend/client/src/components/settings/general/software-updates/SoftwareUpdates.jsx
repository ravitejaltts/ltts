import React from "react";
import { useNavigate } from "react-router-dom";
import { BackIcon } from "../../../../assets/asset";
import SettingRow from "../../../../components/lighting/SettingRow";
import styles from "./software.module.css";

const SoftwareUpdates = ({ data }) => {
  const navigate = useNavigate();
  return (
    <div className={styles.aboutRvContainer}>
      <div className={styles.header}>
        <div className={styles.back} onClick={() => navigate(-1)}>
          <BackIcon />
          <h2>Back</h2>
        </div>
        <p className={styles.heading}>{data?.title}</p>
      </div>
      <div className={styles.container} style={{ marginTop: "40px" }}>
        {data?.data?.map((item, ind, arr) => (
          <React.Fragment key={ind}>
            <SettingRow
              name={item?.title}
              text={item?.value?.version || item?.value}
              bottomText={item?.subtext}
              noBorder={ind === arr.length - 1}
            />
          </React.Fragment>
        ))}
      </div>

      {/* <div className={styles.container} style={{ marginTop: "40px" }}>
        <SettingRow
          name="Software Version"
          text="2.0.1"
          bottomText="Last Updated 2/28/22"
        />
        <SettingRow
          name="Your Coach is Up to date"
          text="Check for updates"
          bottomText="Last checked 2/28/22 2:22pm"
        />
      </div>
      <p className={styles.containerBottomText}>
        Your coach will automatically check for updates and let you know when a
        new version is available
      </p>

      <p className={styles.containerTopText}>Update Options</p>
      <div className={styles.container}>
        <SettingRow name="Automatically Download New Updates" text="" toggle />
        <SettingRow name="Automatically Install New Updates" toggle />
      </div>
      <p className={styles.containerBottomText}>
        Software updates will be installed overnight if the vehicle is parked
        and the battery is sufficiently charged
      </p> */}
    </div>
  );
};

export default SoftwareUpdates;
