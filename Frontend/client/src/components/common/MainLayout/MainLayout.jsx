import React, { useContext, useEffect, useMemo, useState } from "react";
import { AppContext } from "../../../context/AppContext";
import { BACKGROUND_PRIORITY, NOTIFICATION_TYPES, SCREEN_COLOR_NOTIFICATION } from "../../../constants/CONST";
import { MainContext } from "../../../context/MainContext";
import { useFetch } from "../../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../../utils/api";
import SideToolBar from "../SideToolbar/SideBar";
import styles from "./index.module.css";

function MainLayout({ children }) {
  const { pollingInterval, sideBarShow } = useContext(AppContext);
  const { data: notificationApiData } = useFetch(
    API_ENDPOINT.NOTIFICATION,
    LOCAL_ENDPOINT.NOTIFICATION,
    true,
    pollingInterval,
  );
  const [notificationData, setNotificationData] = useState({
    length: 0,
    type: "",
    notifications: [],
  });
  const [bgPriority, setBgPriority] = useState(BACKGROUND_PRIORITY.NOTIFICATION);

  useEffect(() => {
    let value = NOTIFICATION_TYPES.NONE;

    if (bgPriority === BACKGROUND_PRIORITY.NOTIFICATION) {
      if (notificationApiData?.find((item) => item.level === 0)) {
        document.body.style.background = SCREEN_COLOR_NOTIFICATION.CRITICAL;
        value = NOTIFICATION_TYPES.CRITICAL;
      } else if (notificationApiData?.find((item) => item.level === 1)) {
        document.body.style.background = SCREEN_COLOR_NOTIFICATION.WARNING;
        value = NOTIFICATION_TYPES.WARNING;
      } else if (notificationApiData?.find((item) => item.level === 4)) {
        document.body.style.background = SCREEN_COLOR_NOTIFICATION.INFO;
        value = NOTIFICATION_TYPES.INFO;
      } else {
        document.body.style.background = "";
      }
    }
    setNotificationData({
      type: value,
      length: notificationApiData?.length || 0,
      notifications: notificationApiData,
    });
  }, [notificationApiData]);

  const refreshWrapperValue = useMemo(
    () => ({
      notificationData,
      setNotificationData,
      setBgPriority,
    }),
    [notificationData, setNotificationData, setBgPriority],
  );

  return (
    <MainContext.Provider value={refreshWrapperValue}>
      <div className={styles.mainContainer}>
        {sideBarShow && <SideToolBar />}
        <div className={styles.pageContainer}>{children}</div>
      </div>
    </MainContext.Provider>
  );
}

export default MainLayout;
