import { useEffect } from "react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { BackIcon } from "../../../../assets/asset";
import SettingRow from "../../../../components/lighting/SettingRow";
import { getTimeDate } from "../../../constants/helper";
import { SetTimeDialog } from "../set-time-dialog/SetTimeDialog";
import styles from "./time.module.css";

const TimeAndLocation = ({ data }) => {
  const navigate = useNavigate();
  const [timeDialog, setTimeDialog] = useState();
  const [timeZoneScreen, setTimeZoneScreen] = useState(false);
  const [time, setTime] = useState({});

  useEffect(() => {
    const dateTime = getTimeDate();
    let time = dateTime[4].split(" ");
    const [hour, minutes] = time[0].split(":");
    const mode = time[1];
    // console.log(hour, minutes, mode);
    setTime({ hour, minutes, mode });
  }, []);

  const toggleTimeDailog = () => {
    setTimeDialog((prev) => !prev);
  };

  const toggleTimeZoneScreen = () => {
    setTimeZoneScreen((prev) => !prev);
  };

  const changeTime = (newTime) => {
    setTime({ ...newTime });
  };
  return (
    <div className={styles.timeLocationContainer}>
      {!timeZoneScreen ? (
        <>
          <div className={styles.header}>
            <div className={styles.back} onClick={() => navigate(-1)}>
              <BackIcon />
              <h2>Back</h2>
            </div>
            <p className={styles.heading}>{data?.title}</p>
          </div>
          {/* <p className={styles.containerTopText}>Time</p> */}
          {/* <div className={styles.container}>
            <SettingRow name="Automatically Keep Updated" toggle />
          </div>

          <div className={styles.container} style={{ marginTop: "30px" }}>
            <div onClick={toggleTimeZoneScreen}>
              {" "}
              <SettingRow name="Timezone" text="Cental" />
            </div>
            <div onClick={toggleTimeDailog}>
              <SettingRow
                name="Time"
                text={`${time.hour}:${time.minutes} ${time.mode}`}
              />
            </div>
          </div>

          <p className={styles.containerTopText}>Location</p>
          <div className={styles.container}>
            <SettingRow name="Allow WinnConnect to use my Location" toggle />
          </div>
          <p className={styles.containerBottomText}>
            Some additonal details about how the winnconnect system uses your
            location data to the users benifit
          </p>
          {timeDialog && (
            <SetTimeDialog
              close={toggleTimeDailog}
              changeTime={changeTime}
              defaultTime={time}
            />
          )} */}
        </>
      ) : (
        <>
          {/* <div className={styles.header}>
            <div className={styles.back} onClick={toggleTimeZoneScreen}>
              <BackIcon />
              <h2>Back</h2>
            </div>
            <p className={styles.heading}>Timezone</p>
          </div>

          <div className={styles.container} style={{ marginTop: "30px" }}>
            <SettingRow name="Pacific" />
            <SettingRow name="Mountain" />
            <SettingRow name="Central" selected />
            <SettingRow name="Eastern" />
            <SettingRow name="None (set time automatically)" />
          </div> */}
        </>
      )}
    </div>
  );
};

export default TimeAndLocation;
