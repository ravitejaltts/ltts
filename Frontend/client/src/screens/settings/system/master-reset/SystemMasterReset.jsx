import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./index.module.css";
import { BackIcon, Wipe } from "../../../../assets/asset";
import RestartDeviceDialog from "../../../../components/settings/restart-device-dialog/RestartDeviceDialog";
import WipeResetDialog from "../../../../components/settings/wipe-reset-dialog/WipeResetDialog";
import ResettingDialog from "../../../../components/settings/resetting-dialog/ResettingDialog";

const SystemMasterReset = ({ data }) => {
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
      <div className={styles.header}></div>
      <div className={styles.resetBox}>
        <h3 className={styles.title}>{data?.[0]?.title}</h3>
        <p className={styles.description}>{data?.[0]?.subtext}</p>
        <button className={styles.resetBtn} onClick={toggleRestart}>
          {data?.[0]?.data?.[0]?.title}
        </button>
        <p className={styles.lastBackup}>{data?.[0]?.bottomtext}</p>
      </div>
      <button className={styles.removeUser} onClick={toggleWipe}>
        Reset Without Backup
      </button>

      {wipe && (
        <WipeResetDialog
          data={data?.[0]?.data?.[0]?.data?.[0]?.data?.[1]}
          close={toggleWipe}
          open={toggleReset}
        />
      )}
      {restart && (
        <RestartDeviceDialog
          data={data?.[0]?.data?.[0]?.data?.[0]?.data?.[2]}
          close={toggleRestart}
        />
      )}
      {reset && <ResettingDialog close={toggleReset} />}
    </div>
  );
};

export default SystemMasterReset;
