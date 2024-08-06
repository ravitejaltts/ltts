import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../../../context/AppContext";
import {
  BellGray,
  BellWhite,
  BluetoothConnected,
  BluetoothDisabled,
  BluetoothReady,
  BluetoothSearching,
  WifiFour,
  WifiNone,
  WifiOne,
  WifiThree,
  WifiTwo,
} from "../../../assets/asset";
import useLongPress from "../../../hooks/useLongPress";
import { getTimeDate } from "../../constants/helper";
import styles from "./header.module.css";
import { PAGE_LINKS } from "../../../constants/CONST";

const WifiComponent = (icon) => {
  const value = icon?.data.data[0]?.value;
  if (icon.data.status === "active") {
    return (
      <>
        {value === "1" ? (
          <WifiOne className={styles.headerIcon} />
        ) : value === "2" ? (
          <WifiTwo className={styles.headerIcon} />
        ) : value === "3" ? (
          <WifiThree className={styles.headerIcon} />
        ) : (
          value === "4" && <WifiFour className={styles.headerIcon} />
        )}
      </>
    );
  } else {
    return <WifiNone className={styles.headerIcon} />;
  }
};
const BtComponent = (icon) => {
  const value = icon?.data.data[0]?.key;
  if (icon.data.status === "active") {
    return (
      <>
        {value === "BT_CONNECTED_DEVICE" ? (
          <BluetoothConnected className={styles.headerIcon} />
        ) : value === "BT_SEARCHING" ? (
          <BluetoothSearching className={styles.headerIcon} />
        ) : (
          value === "BT_READY" && (
            <BluetoothReady className={styles.headerIcon} />
          )
        )}
      </>
    );
  } else {
    return <BluetoothDisabled className={styles.headerIcon} />;
  }
  // return <BluetoothConnected className={styles.headerIcon} />;
};
const NotificationComponent = ({ data, setIndex, index }) => {
  if (data.status === "active") {
    return (
      <>
        <BellWhite
          onClick={() => setIndex(index + 1)}
          className={styles.headerIcon}
        />
        {Number(data?.data[1].value) > 0 ? (
          <span className={styles.badgeCritical}>{data?.data[0].value}</span>
        ) : Number(data?.data[2].value) > 0 ? (
          <span className={styles.badgeWarning}>{data?.data[0].value}</span>
        ) : Number(data?.data[3].value) > 0 ? (
          <span className={styles.badgeInfo}>{data?.data[0].value}</span>
        ) : (
          <span className={styles.badgeNone}>0</span>
        )}
      </>
    );
  } else {
    return (
      <BellGray
        onClick={() => setIndex(index + 1)}
        className={styles.headerIcon}
      />
    );
  }
};

const Header = ({ setIndex, index, data, timeZone }) => {
  const [time, setTime] = useState();
  const navigate = useNavigate();
  const { toggleTheme } = useContext(AppContext);

  useEffect(() => {
    dataFetching();
  }, [data]);

  const dataFetching = async () => {
    const timeData = getTimeDate();
    setTime(timeData);
  };
  const onLongPress = () => {
    // navigate("http://127.0.0.1:8000/testing/wgo.html");
    // window.location.href = "http://127.0.0.1:8000/testing/wgo.html";
  };

  const onClick = () => {
    // action();
    navigate(PAGE_LINKS.SETTINGS);
  };

  const defaultOptions = {
    shouldPreventDefault: true,
    delay: 500,
  };
  const longPressEventSettings = useLongPress(
    onLongPress,
    onClick,
    defaultOptions
  );

  const lockScreen = () => {
    localStorage.setItem("passcodeEntered", "false");
    navigate("/locked");
  };

  const fullscreen = () => {
    // Supports most browsers and their versions.
    var elem = document.body;
    var requestMethod =
      elem.requestFullScreen ||
      elem.webkitRequestFullScreen ||
      elem.mozRequestFullScreen ||
      elem.msRequestFullScreen;

    if (requestMethod) {
      // Native full screen.
      requestMethod.call(elem);
    }
  };

  return (
    <div className={styles.header}>
      {time && (
        <div className={styles.date} id="home-time" onClick={fullscreen}>
          {time[0]} {time[1]} {time[2]}
          <span className={styles.time}> {time[4]} </span>
        </div>
      )}
      {data?.icons?.map((icon) => (
        <div key={icon.name} style={{ position: "relative" }}>
          {icon.name === "TopWifi" ? (
            <WifiComponent data={icon} />
          ) : icon.name === "TopBluetooth" ? (
            <BtComponent data={icon} />
          ) : (
            icon.name === "TopNotifications" && (
              <NotificationComponent
                data={icon}
                setIndex={setIndex}
                index={index}
              />
            )
          )}
        </div>
      ))}
      {/* Manually Disable the lock button on home screen */}
      {/* <div>
        <Lock onClick={lockScreen} />
      </div> */}
      {/* <div id="home-bt-icon-3">
        <SettingsIcon {...longPressEventSettings} className="icon" />
      </div> */}
    </div>
  );
};

export default Header;
