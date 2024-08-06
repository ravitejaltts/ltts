import axios from "axios";
import React, { useState } from "react";
import SettingRow from "../../lighting/SettingRow";
import styles from "./index.module.css";
import StartPairing from "./start-pairing/StartPairing";

const Bluetooth = ({ data }) => {
  const [state, setState] = useState(true);
  // const navigate = useNavigate();
  // const navigateTo = (url) => navigate(url);
  const restart = async () => {
    axios
      .put("/api/system/service/ble/restart")
      .then((res) => {
        // success callback
      })
      .catch((err) => {
        console.error(err);
      });
  };

  return (
    <div className={styles.container}>
      <h2 className={styles.mainTitle}>{data?.title}</h2>
      {state ? (
        <>
          {data?.data?.configuration?.map((config, i) => (
            <>
              {config?.title && (
                <p className={styles.infoContainerTopText}>{config?.title}</p>
              )}
              <div key={i} className={styles.infoContainer}>
                {config?.data?.map((configItem, i, arr) => (
                  <div key={i}>
                    <div>
                      <SettingRow
                        name={configItem?.title}
                        toggle={configItem?.Simple ? true : false}
                        arrow={configItem?.Simple ? false : true}
                        noBorder={i === arr.length - 1}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </>
          ))}
          {/* <div className={styles.infoContainer}>
            <div>
              <SettingRow name="Enable control through Bluetooth" toggle />
            </div>
            <div>
              <SettingRow name="Bluetooth SSID" arrow />
            </div>
          </div>
          <p className={styles.infoContainerTopText}>USERS</p>
          <div className={styles.infoContainer}>
            <div onClick={() => navigateTo("user-detail")}>
              <SettingRow name="Barret Hoster" arrow />
            </div>
            <div onClick={() => navigateTo("user-detail")}>
              <SettingRow name="Joe Lalonde" arrow />
            </div>
            <div onClick={() => navigateTo("user-detail")}>
              <SettingRow name="Ryan Bowman" arrow />
            </div>
          </div> */}

          <button
            className={styles.pairNewUser}
            onClick={() => setState(false)}
          >
            Pair a New User
          </button>
        </>
      ) : (
        <StartPairing />
      )}
      <button className={styles.resetBtn} onClick={restart}>
        Restart Bluetooth
      </button>
    </div>
  );
};

export default Bluetooth;
