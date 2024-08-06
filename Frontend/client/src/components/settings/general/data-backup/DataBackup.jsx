import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { BackIcon } from "../../../../assets/asset";
import DetailRow from "../../../common/detail-row/DetailRow";
import BackingUpDialog from "../backing-up-dialog/BackingUpDialog";
import styles from "./index.module.css";

const DataBackup = ({ data }) => {
  const [backup, setBackup] = useState(false);
  const navigate = useNavigate();
  // const navigateTo = (url) => navigate(url);

  const toggleBackup = () => {
    setBackup((prev) => !prev);
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
      <div className={styles.contentContainer}>
        <div className={styles.infoContainer}>
          {data?.data?.map((item, ind) => (
            <React.Fragment key={ind}>
              {item?.data?.map((dat, i) => (
                <React.Fragment key={i}>
                  {dat?.Simple ? (
                    <div>
                      <DetailRow
                        name={dat?.title}
                        bottomText={dat?.subtext}
                        toggle
                        toggleState={dat?.Simple?.onOff}
                        toggleAction={dat?.action_default?.action}
                      />
                    </div>
                  ) : (
                    <DetailRow
                      name={dat?.title}
                      text="Sync Now"
                      bottomText={dat?.subtext}
                      buttonAction={dat?.action_default?.action}
                    />
                  )}
                </React.Fragment>
              ))}
            </React.Fragment>
          ))}
        </div>

        {/* <p className={styles.infoText}>
          WinnConnect saves your system preferences and presets for easy backup
        </p>
        <button className={styles.restoreBackup} onClick={toggleBackup}>
          Restore from Pevious Backup
        </button> */}
      </div>
      {/* {backup && <BackingUpDialog close={toggleBackup} />} */}
    </div>
  );
};

export default DataBackup;
