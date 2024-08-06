import { useContext, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../../context/AppContext";
import Header from "../../components/home/header/Header";
import Notification from "../../components/home/notificationBox/Notification";
import NotificationIcon from "../../components/home/notificationIcon/NotificationIcon";
import { DataContext } from "../../context/DataContext";
import { useFetch } from "../../hooks/useFetch";
import useLocalStorage from "../../hooks/useLocalStorage";
import useSwipe from "../../hooks/useSwipe";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../utils/api";
import styles from "./home.module.css";
import PetWidget from "../../components/home/pet-widget/PetWidget";
import PetNotification from "../../components/home/pet-notification/PetNotification";
import HomeBottomWidgets from "./HomeBottomWidgets";

function Home() {
  const navigate = useNavigate();

  const { pollingInterval, setTheme } = useContext(AppContext);
  const { data: homeData, refreshDataImmediate } = useFetch(
    API_ENDPOINT.HOME,
    LOCAL_ENDPOINT.HOME,
    true,
    pollingInterval,
  );
  const topValue = useRef(0);
  const [handleTouchStart, handleTouchMove, handleTouchEnd] = useSwipe(150, leftSwipe, rightSwipe);
  const [contentType, setContentType] = useState(1);
  const [index, setIndex] = useState(0);
  const notificationRef = useRef(false);
  const [, setHomeSettings] = useLocalStorage(LOCAL_ENDPOINT.HOME_SETTINGS, null);

  function leftSwipe() {
    navigate("/my-rv");
  }

  function rightSwipe() {
    navigate("slider");
  }

  const toggleContent = (num) => {
    if (contentType === num) {
      setContentType(1);
    } else {
      setContentType(num);
    }
  };

  useEffect(() => {
    if (homeData) {
      navigate("/");
    }
    if (homeData?.redirect) {
      navigate(homeData?.redirect);
    }
    if (homeData?.settings?.screenMode) {
      setTheme(homeData?.settings?.screenMode);
    }
    setHomeSettings(homeData?.settings);
  }, [homeData]);

  const refreshWrapperValue = useMemo(() => ({ refreshParentData: refreshDataImmediate }), [refreshDataImmediate]);

  return (
    <DataContext.Provider value={refreshWrapperValue}>
      {homeData && (
        <div
          className={styles.container}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
          id="home-container"
        >
          <div className={styles.topRow} id="home-top-row">
            <div className={styles.weatherIcon} id="home-weather-icon">
              <div className={styles.iconBar}>
                {homeData?.petmonitoring ? <PetWidget data={homeData?.petmonitoring} /> : <NotificationIcon />}
              </div>
            </div>
            <div className={styles.widgetBar} id="home-widgetbar">
              <Header index={index} setIndex={setIndex} toggleContent={toggleContent} data={homeData?.top} />
            </div>
          </div>
          <div className={styles.middleRow} id="home-main-box">
            {homeData?.petmonitoring?.status ? (
              <PetNotification data={homeData?.petmonitoring?.status} refreshDataImmediate={refreshDataImmediate} />
            ) : (
              <Notification
                index={index}
                setIndex={setIndex}
                defaultMsg={homeData?.motd}
                notificationRef={notificationRef}
              />
            )}
          </div>
          <div className={styles.bottomRow} id="home-bottom-row">
            <HomeBottomWidgets homeData={homeData} topValue={topValue} />
          </div>
        </div>
      )}
    </DataContext.Provider>
  );
}

export default Home;
