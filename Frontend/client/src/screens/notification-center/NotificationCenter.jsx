import axios from "axios";
import React, { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import { SettingArrow } from "../../assets/asset";
import { CloseNotification, NoNotification } from "../../assets/assets";
import ClearAllNotificationModal from "../../components/notification-center/clear-notification-modal/ClearAllNotificationModal";
import BackButton from "../../components/settings/back-button/BackButton";
import AlertIcon from "./AlertIcon";
import AlertIconBox from "./AlertIconBox";
import styles from "./noti-center.module.css";
import { AppContext } from "../../context/AppContext";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../utils/api";
import { useFetch } from "../../hooks/useFetch";
import StatusAlertDetails from "./statusAlertDetails/StatusAlertDetails";

const NotificationCenter = () => {
  const [statusAlertDetails, setStatusAlertDetail] = useState(null);
  const { pollingInterval } = useContext(AppContext);
  const { data: notificationData, refreshDataImmediate } = useFetch(
    API_ENDPOINT.NOTIFICATION_CENTER,
    LOCAL_ENDPOINT.NOTIFICATION_CENTER,
    true,
    pollingInterval,
  );
  const navigate = useNavigate();
  const [clearNotificationModal, setClearNotificationModal] = useState(false);
  function openClearModal() {
    setClearNotificationModal(true);
  }
  function handleClose() {
    setClearNotificationModal(false);
  }

  function handleClearAllApi() {
    if (notificationData?.data?.[2]?.actions?.CLEAR_ALL?.action?.href) {
      axios
        .put(notificationData?.data?.[2]?.actions?.CLEAR_ALL?.action?.href, {
          onOff: 1,
        })
        .then((res) => {
          handleClose();
        });
    }
  }

  const clearNotification = (notification) => {
    const action = notification?.actions?.clear_notification?.action;
    axios.put(action?.href).then(() => refreshDataImmediate());
  };

  console.log("notificationData", notificationData);

  const getPriority = (priority) => {
    console.log("pp", priority);
    if (priority <= 1) {
      return "critical";
    } else if (priority <= 3) {
      return "warning";
    } else if (priority >= 4) {
      return "information";
    }
  };

  return (
    <>
      {statusAlertDetails ? (
        <StatusAlertDetails alert={statusAlertDetails} setStatusAlertDetail={setStatusAlertDetail} />
      ) : (
        <div className={styles.container}>
          <div className={styles.header}>
            <div className={styles.back}>
              <BackButton handler={() => navigate(-1)} />
            </div>
            <span className={styles.heading}>Notifications</span>
          </div>
          <div className={styles.content}>
            {notificationData?.data[0]?.data?.length === 0 && notificationData?.data[1]?.data?.length === 0 ? (
              <div className={styles.noData}>
                <NoNotification />
                <p className={styles.noNotificationTitle}>No Notifications</p>
                <p className={styles.subtext}>
                  You have no notifications!
                  <br />
                  Good job!
                </p>
              </div>
            ) : (
              <div className={styles.mainContent}>
                <div className={styles.alertContainer}>
                  <p className={styles.alertHeading}>{notificationData?.data?.[0]?.title}</p>
                  {notificationData?.data?.[0]?.data?.length !== 0 ? (
                    notificationData?.data?.[0]?.data?.map((alert, ind) => (
                      <div className={styles.alertBox} key={ind} onClick={() => setStatusAlertDetail(alert)}>
                        <AlertIcon priority={alert?.priority} />

                        <div className={styles.alertContent}>
                          <p className={styles.statusHeading}>{alert?.header}</p>
                          <p className={styles.link}>Learn More</p>
                        </div>
                        <div className={styles.backIcon}>
                          <SettingArrow />
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className={styles.noAlerts}>No current Status Alerts</p>
                  )}
                </div>
                <div>
                  <div className={styles.subheader}>
                    <p className={styles.alertHeading}>{notificationData?.data?.[1]?.title}</p>
                    <p
                      className={`${styles.clearAll} ${
                        notificationData?.data?.[1]?.data?.length ? "" : styles.disabled
                      }`}
                      onClick={() => {
                        !!notificationData?.data?.[1]?.data?.length && openClearModal();
                      }}
                    >
                      {notificationData?.data?.[2]?.subtext}
                    </p>
                  </div>
                  {notificationData?.data?.[1]?.data?.length !== 0 ? (
                    notificationData?.data?.[1]?.data?.map((noti, ind) => (
                      <div className={styles.generalCardContainer} key={ind}>
                        {!!noti.active && <div className={styles.activeNoti} />}
                        <div className={styles.generalCard}>
                          <div className={styles.header2}>
                            <div className={styles.header2Content}>
                              <AlertIconBox type={noti?.priority} active={!!noti.active} />
                              <p className={styles.notiheading}>{noti?.header}</p>
                            </div>
                            <p className={styles.time}>Today, 00:00 PM</p>
                          </div>
                          <p className={styles.notiContent}>{noti?.message}</p>
                        </div>
                        <CloseNotification className={styles.closeIcon} onClick={() => clearNotification(noti)} />
                      </div>
                    ))
                  ) : (
                    <p className={styles.noAlerts}>No current General Notifications</p>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {clearNotificationModal && <ClearAllNotificationModal close={handleClose} onClear={handleClearAllApi} />}
    </>
  );
};

export default NotificationCenter;
