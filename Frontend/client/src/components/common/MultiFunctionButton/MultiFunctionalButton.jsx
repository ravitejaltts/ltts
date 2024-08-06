import { useEffect, useRef, useState } from "react";
import styles from "./button.module.css";

export default function MultiFunctionalButton({
  children,
  longPressCallback = () => {
    // console.log("Long press");
  },
  onClickCb = () => {
    // console.log("click");
  },
  onReleaseCb = () => {
    // console.log("release");
  },
  disabled = false,
  holdDelayTime,
  apiCallIntervalTime,
  animateColor = "#4c85a9",
  deadmanState,
  handleDeadman,
  id,
}) {
  const timerRef = useRef(null);
  const apiCallRef = useRef(null);
  const [clickState, setClickState] = useState(false);
  const [longPressedState, setLongPressedState] = useState(false);
  const [touchIdentifier, setTouchIdentifier] = useState(null);

  // touchIdentifier represents the number of touches at the moments start with 0 indexing

  const handleOnClick = (e) => {
    if (touchIdentifier === null || e?.changedTouches?.[0]?.identifier === touchIdentifier) {
      clearTimeout(apiCallRef.current);

      setLongPressedState(false);
      setClickState(true);
    }
  };

  const handleOnPressStart = (e) => {
    // console.log("press start");
    if (touchIdentifier === null || e?.changedTouches?.[0]?.identifier === touchIdentifier) {
      setTouchIdentifier(e?.changedTouches?.[0]?.identifier);
      if (!longPressedState && holdDelayTime !== null) {
        setLongPressedState(false);
        setClickState(false);
        clearInterval(timerRef.current);
        handleDeadman(id);
        apiCallRef.current = setTimeout(() => {
          setLongPressedState(true);
        }, holdDelayTime);
      } else if (!longPressedState && holdDelayTime === null) {
        setLongPressedState(false);
        setClickState(false);
        clearInterval(timerRef.current);
        handleDeadman(id);
        apiCallRef.current = setTimeout(() => {
          setLongPressedState(true);
        }, 0);
      }
    }
  };

  const handleOnPressEnd = (e) => {
    // console.log("press end");
    if (touchIdentifier === null || e?.changedTouches?.[0]?.identifier === touchIdentifier) {
      setTouchIdentifier(null);
      clearTimeout(apiCallRef.current);
      clearInterval(timerRef.current);
      setLongPressedState(false);
      handleDeadman(null);
      if (longPressedState) {
        onReleaseCb();
      }
    }
  };

  useEffect(() => {
    if (longPressedState) {
      longPressCallback();
      if (apiCallIntervalTime) {
        timerRef.current = setInterval(() => {
          if (longPressedState) {
            longPressCallback();
          }
        }, apiCallIntervalTime);
      }
    } else {
      clearInterval(timerRef.current);
    }
    return () => {
      clearInterval(timerRef.current);
    };
  }, [longPressedState]);

  useEffect(() => {
    let timer;
    if (clickState) {
      onClickCb();
      timer = setTimeout(() => {
        setClickState(false);
      }, holdDelayTime);
    }
    return () => {
      clearTimeout(timer);
    };
  }, [clickState]);

  useEffect(() => {
    if (!deadmanState) {
      clearInterval(timerRef.current);
      clearTimeout(apiCallRef.current);
      setClickState(false);
      setLongPressedState(false);
    }
  }, [deadmanState]);

  useEffect(() => {
    return () => {
      handleDeadman(null);
    };
  }, []);

  function getDisabledClass() {
    return disabled ? styles.disabled : "";
  }

  return (
    <div
      className={`${styles.mainContainer} ${getDisabledClass()} m-auto`}
      style={{ "--deadman-border-animation": animateColor }}
    >
      <div
        onClick={handleOnClick}
        onTouchStart={handleOnPressStart}
        onTouchEnd={handleOnPressEnd}
        className={`${styles.container} `}
      >
        <div style={{ opacity: clickState ? 0 : 1 }}>{children}</div>
        {clickState && holdDelayTime && (
          <div className={styles.infoContainer}>
            <div className={styles.inActive}>Press and Hold for 1 second</div>
          </div>
        )}

        {longPressedState && <div className={styles.animate} />}
      </div>
      {disabled || (clickState && <div className={styles.disabledBox} />)}
    </div>
  );
}
