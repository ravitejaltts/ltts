import React from "react";
import { useNavigate } from "react-router-dom";
import { BackIcon } from "../../../../assets/asset";
import SettingRow from "../../../lighting/SettingRow";
import styles from "./index.module.css";

const UserDetail = () => {
  const navigate = useNavigate();
  // const navigateTo = (url) => navigate(url);
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.back} onClick={() => navigate(-1)}>
          <BackIcon />
          <h2>Back</h2>
        </div>
        <h2 className={styles.mainTitle}>User Detail</h2>
      </div>
      <p className={styles.infoContainerTopText}>ACCOUNT INFORMATION</p>
      <div className={styles.infoContainer}>
        <div>
          <SettingRow name="Name" text="Barret Hoster" />
        </div>
        <div>
          <SettingRow name="Email" text="bhoster@ostusa.com" />
        </div>
      </div>
      <p className={styles.infoContainerTopText}>DEVICE</p>
      <div className={styles.infoContainer}>
        <div>
          <SettingRow name="Device Name" text="Barret’s iPhone" />
        </div>
        <div>
          <SettingRow name="Last Paired" text="Tues May 3 10:18AM" />
        </div>
        <div>
          <SettingRow name="Name" text="Barret Hoster" />
        </div>
      </div>
      <button className={styles.removeUser}>Remove User</button>
    </div>
  );
};

export default UserDetail;
