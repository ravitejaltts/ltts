import axios from "axios";
import { useNavigate } from "react-router-dom";
import React, { useContext, useEffect, useState } from "react";
import { AppContext } from "../../../context/AppContext";
import { useFetch } from "../../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../../utils/api";
import styles from "./noti.module.css";

function Notification({ index, setIndex, defaultMsg, notificationRef }) {
  const { pollingInterval } = useContext(AppContext);
  const navigate = useNavigate();
  const doNavigation = (href) => {
    navigate(href);
  };
  const { data: tempData, refreshDataImmediate } = useFetch(
    API_ENDPOINT.NOTIFICATION,
    LOCAL_ENDPOINT.NOTIFICATION,
    true,
    pollingInterval,
  );
  const [data, setData] = useState(null);

  useEffect(() => {
    // TODO: does "notificationRef.current = tempData" have side-effects that we rely on? Try something else.
    // eslint-disable-next-line no-param-reassign
    notificationRef.current = tempData;
    if (tempData?.length === 0) {
      setData([]);
      setIndex(0);
    }
    if (index >= tempData?.length) {
      setIndex(0);
    } else {
      setData((prev) => {
        // this is done in setData because of closures data have value of undefined in setInterval
        // 1 condition to check if the any new mesage is added to notification api
        // 2 check if index num if greater that num of notification message rest it to 0 so suupose 4 message counter should go like 0,1,2,3,0,1,2,3
        if (prev) {
          if (prev[0]?.header !== tempData[0]?.header) {
            setIndex(0);
          }
        }

        return tempData;
      });
    }
  }, [tempData]);

  const action = (type) => {
    console.log(`Notification.Action ${type}`);
    if (type === "dismiss") {
      try {
        axios
          .get(`ui${data[index]?.footer[`action_${type}`]?.action?.event_href}`)
          .finally(() => refreshDataImmediate());
      } catch (e) {
        console.error(e);
      }
    } else if (type === "navigate") {
      const path = data[index]?.footer[`action_${type}`]?.action?.href;
      doNavigation(path);
    } else if (type === "api_call") {
      const path = data[index]?.footer[`action_${type}`]?.action?.href;
      const params = data[index]?.footer[`action_${type}`]?.action?.params;
      try {
        axios.put(path, params);
      } catch (e) {
        console.error(e);
      }
    } else {
      console.error(`Unsupported action type: ${type}`);
    }
  };

  return (data || []).length ? (
    <>
      <p id="home-temp-text" className={styles.title} style={{ opacity: 0.8 }}>
        {data[index]?.header && data[index]?.header}
      </p>
      <p id="home-temp-desc-text" className={styles.weatherDesc}>
        {data[index]?.body}
      </p>
      <div id="home-forecast-div" style={{ display: "flex", alignItems: "center" }} className={styles.footer}>
        {data[index]?.footer?.actions?.map((btn) => (
          <button type="button" className={styles.btn1} key={btn} onClick={() => action(btn)}>
            <span className={styles.btnText}>{data[index]?.footer[`action_${btn}`]?.action?.text}</span>
          </button>
        ))}
      </div>
    </>
  ) : (
    <>
      <p id="home-temp-text" className={styles.title} style={{ opacity: 0.8 }}>
        {defaultMsg?.title}
      </p>
      <p id="home-temp-desc-text" className={styles.weatherDesc}>
        {defaultMsg?.text}
      </p>
    </>
  );
}

export default Notification;
