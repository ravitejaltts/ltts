import NotificationsActiveIcon from "@mui/icons-material/NotificationsActive";
import React from "react";
import { Link } from "react-router-dom";
import styles from "./noti.module.css";

const Notification = ({ setNotification }) => {
  return (
    <div className={styles.notification}>
      <NotificationsActiveIcon
        className={styles.notificationIcon}
        style={{ marginBottom: "20px" }}
      />
      <p className={styles.heading}>
        Sample of <br /> a Notification
      </p>
      <p className={styles.content}>
        This is an example of how a notification would display.
      </p>
      <div className={styles.btnContainer}>
        <button
          className={styles.notBtn}
          onClick={() => setNotification(false)}
        >
          Not Now
        </button>
        <Link to="/warning">
          <button className={styles.okayBtn}>Okay</button>
        </Link>
      </div>
    </div>
  );
};

export default Notification;
