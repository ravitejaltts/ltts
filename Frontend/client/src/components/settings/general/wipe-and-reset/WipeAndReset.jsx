import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { BackIcon } from "../../../../assets/asset";
import styles from "./index.module.css";

const WipeAndReset = ({ data }) => {
  const [wipe, setWipe] = useState(false);
  const [restart, setRestart] = useState(false);
  const [reset, setReset] = useState(false);
  const navigate = useNavigate();
  // const navigateTo = (url) => navigate(url);

  const toggleWipe = () => {
    setWipe((prev) => !prev);
  };
  const toggleRestart = () => {
    setRestart((prev) => !prev);
  };
  const toggleReset = () => {
    setWipe(false);
    setReset((prev) => !prev);
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.back} onClick={() => navigate(-1)}>
          <BackIcon />
          <h2>Back</h2>
        </div>
        <h2 className={styles.mainTitle}>{data?.title}</h2>
      </div>
      {/* <div className={styles.resetBox}>
        <Wipe />
        <h3 className={styles.title}>Resetting WinnConnect</h3>
        <p className={styles.description}>
          Resetting your WinnConnect system clears all locally stored data and
          restores your system to factory defaults. You can save a back up of
          your configuration preferences to restore after reset (does not
          include WiFi or Bluetooth configurations) .
        </p>
        <button className={styles.resetBtn} onClick={toggleRestart}>
          Backup and Reset
        </button>
        <p className={styles.lastBackup}>Last backup May 2, 2022 12:23pm</p>
      </div>
      <button className={styles.removeUser} onClick={toggleWipe}>
        Reset Without Backup
      </button>

      {wipe && <WipeResetDialog close={toggleWipe} open={toggleReset} />}
      {restart && <RestartDeviceDialog close={toggleRestart} />}
      {reset && <ResettingDialog close={toggleReset} />} */}
    </div>
  );
};

export default WipeAndReset;
