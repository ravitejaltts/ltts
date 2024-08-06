import axios from "axios";
import React, { useEffect, useState } from "react";
import { BackIcon, Close } from "../../../assets/asset";
import Switch from "../../common/switch/Switch";
import EventSetting from "../event-setting/EventSetting";
import SchedulerRow from "../schedule-row/SchedulerRow";
import styles from "./scheduler.module.css";

const defaultTime = {
  Wake: {
    hour: 6,
    minutes: 0,
    mode: "AM",
  },
  Away: {
    hour: 9,
    minutes: 0,
    mode: "AM",
  },
  "At Camp": {
    hour: 5,
    minutes: 0,
    mode: "PM",
  },
  Sleep: {
    hour: 10,
    minutes: 0,
    mode: "PM",
  },
};

const Scheduer = ({ handleClose, clearSchedule }) => {
  const [showPopup, setPopup] = useState(true);
  const [showDetails, setShowDetails] = useState(false);
  const [activeData, setActiveData] = useState();
  const [data, setData] = useState();
  const [param, setParam] = useState({});
  useEffect(() => {
    dataFetching();
  }, []);

  useEffect(() => {
    const obj = {
      id: activeData?.id,
      setTempHeat: activeData?.setTempHeat || 60,
      setTempCool: activeData?.setTempCool || 80,
      startHour: activeData?.startHour || defaultTime[activeData?.title]?.hour,
      startMinute:
        activeData?.startMinute || defaultTime[activeData?.title]?.minutes,
      startTimeMode:
        activeData?.startTimeMode || defaultTime[activeData?.title]?.mode,
    };
    setParam(obj);
  }, [activeData, showDetails]);

  const dataFetching = () => {
    axios.get("ui/climate/schedule").then((res) => {
      setData(res.data);
    });
  };

  const openDetails = (id) => {
    setActiveData(data?.items[id]);
    setShowDetails(true);
  };

  const toggleDetailModal = () => {
    setShowDetails((prev) => !prev);
  };
  const clearEvent = (id) => {
    clearSchedule(id);
    toggleDetailModal();
  };

  const saveSchedule = () => {
    axios
      .put(data?.action_set?.action?.href, param)
      .then((res) => {
        setShowDetails(false);
      })
      .catch((err) => {
        console.log(err);
      });
  };

  const changeParam = (type, value) => {
    let newObj = { ...param };
    newObj[type] = value;
    console.log("Params Change", param);
    setParam(newObj);
  };

  return (
    <div className={styles.settings}>
      {showDetails ? (
        <div>
          <div className={styles.header}>
            <div className={styles.back} onClick={() => setShowDetails(false)}>
              <BackIcon />
              <h2>Back</h2>
            </div>
            <p className={styles.heading}>Event Setting</p>
            <div className={styles.saveBtn} onClick={saveSchedule}>
              Save
            </div>
          </div>

          <div className={styles.infoContainer}>
            <EventSetting
              id={activeData?.id}
              title={activeData?.title}
              param={param}
              changeParam={changeParam}
              clearEvent={clearEvent}
            />
          </div>
        </div>
      ) : (
        <div className={styles.max}>
          <div className={styles.header}>
            <Close onClick={handleClose} className={styles.closeIcon} />
            <p className={styles.heading}>Schedule</p>
            <Switch
              onOff={data?.Simple.onOff}
              action={data?.action_default?.action}
            />
          </div>

          <div className={styles.infoContainer}>
            {data?.items.map((item, index) => (
              <div key={index} onClick={() => openDetails(item?.id)}>
                <SchedulerRow {...item} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Scheduer;
