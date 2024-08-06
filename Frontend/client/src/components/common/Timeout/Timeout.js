import axios from "axios";
import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../../../context/AppContext";
import { IDLE_TIME_DEFAULT, OFF_TIME_DEFAULT, POLLING_INTERVAL } from "../../constants/timer";
import Timer from "../Timer/Timer";
import styles from "./timeout.module.css";

function Timeout({ setPollingInterval }) {
  const [data] = useState();
  const [idle, setIdle] = useState(null);
  const [off, setOff] = useState(null);
  const [idleTimer, setIdleTimer] = useState(false);
  const [offTimer, setOffTimer] = useState(false);
  const { setAnimate } = useContext(AppContext);
  const navigate = useNavigate();
  const timerFetch = async () => {
    const res = await axios.get("/ui/home").then((res) => {
      if (res.data.settings.activity) {
        setPollingInterval(res.data.settings.activity.activePollingInterval);
      } else {
        setPollingInterval(POLLING_INTERVAL);
      }
    });

    if (res?.inactiveTimeout) {
      setIdleTimer((res?.inactiveTimeout || 0) * 1000);
    } else {
      setIdleTimer(IDLE_TIME_DEFAULT * 1000);
    }
    if (res?.offTimeout) {
      setOffTimer((res?.offTimeout || 0) * 1000);
    } else {
      setOffTimer(OFF_TIME_DEFAULT * 1000);
    }
  };
  // };
  useEffect(() => {
    timerFetch();
  }, []);
  useEffect(() => {
    if (data) {
      if (idle === true) {
        console.log(data?.activityAPIs?.inactive);
        axios.put(data?.activityAPIs?.inactive).catch((err) => console.log(err));
      } else {
        console.log(data?.activityAPIs?.active);
        setAnimate(true);
        setPollingInterval(data.activePollingInterval);
        axios.put(data?.activityAPIs?.active).catch((err) => console.log(err));
      }
    }
  }, [idle, setAnimate, setPollingInterval, data]);
  useEffect(() => {
    if (data) {
      if (off === true && idle === true) {
        setPollingInterval(data.offPollingInterval);
        console.log("Timeout false");
        axios
          .put(data?.activityAPIs?.off)
          .then(() => {
            if (data.isProtected) {
              navigate("/locked");
            }
            setAnimate(false);
          })
          .catch((err) => console.log(err));
      }
    }
  }, [off]);

  const handleActivity = (e) => {
    setIdle(false);
    setOff(false);
    e.preventDefault();
    e.stopPropagation();
  };

  return (
    <>
      {data && <Timer timeout={idleTimer} setter={setIdle} />}
      {data && idle && <Timer timeout={offTimer} setter={setOff} />}
      {idle && <div className={styles.overlay} onTouchEnd={handleActivity} />}
    </>
  );
}

export default Timeout;
