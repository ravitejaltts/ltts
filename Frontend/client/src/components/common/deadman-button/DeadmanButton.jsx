import { useEffect, useRef, useState } from "react";
import styles from "./deadman-button.module.css";

export default function DeadmanButton(inputs) {
  const {
    children,
    longPressCallback = () => {},
    onClickCb = () => {},
    onReleaseCb = () => {},
    holdDelayTime = 1000,
    animateColor = "#4c85a9",
    deadmanState,
    handleDeadman,
    id,
  } = inputs;
  let { disabled } = inputs;
  const [isHolding, setIsHolding] = useState(false);
  const [isWarning, setIsWarning] = useState(false);
  const holdTimeout = useRef(null);
  const warningTimeout = useRef(null);

  const onTouchStart = (event) => {
    event.stopPropagation();
    if (isWarning) {
      setWarningTimer();
    }
    if (disabled) {
      return;
    }
    setHoldTimer(holdDelayTime);
  };

  const onTouchEnd = (event) => {
    event.stopPropagation();
    if (isHolding) {
      setWarningTimer();
    }
    clearTimeout(holdTimeout.current);
    holdTimeout.current = null;
    setIsHolding(false);
    onReleaseCb();
  };

  const onClick = (event) => {
    event.stopPropagation();
    if (disabled) {
      return;
    }
    onClickCb();
  };

  function setHoldTimer(duration = 1000) {
    setIsHolding(true);
    disabled = true;
    holdTimeout.current = setTimeout(() => {
      setIsHolding(false);
      handleDeadman(id);
      disabled = false;
      longPressCallback();
    }, duration);
  }

  function setWarningTimer(duration = 1300) {
    clearTimeout(warningTimeout.current);
    setIsWarning(true);
    warningTimeout.current = setTimeout(() => {
      setIsWarning(false);
    }, duration);
  }

  useEffect(() => {
    // Cleanup on unmount
    return () => {
      setIsHolding(false);
      setIsWarning(false);
    };
  }, []);

  useEffect(() => {
    if (!deadmanState) {
      clearTimeout(holdTimeout.current);
      setIsHolding(false);
    }
  }, [deadmanState]);

  function getDisabledClass() {
    return disabled ? styles.disabled : "";
  }

  return (
    <div
      className={`${styles.mainContainer} m-auto ${getDisabledClass()}`}
      style={{ "--deadman-border-animation": animateColor }}
    >
      <button
        type="button"
        onClick={onClick}
        onTouchStart={onTouchStart}
        onTouchEnd={onTouchEnd}
        className={`${styles.container} no-btn`}
        disabled={disabled}
      >
        <div>{children}</div>
        <div className={styles.warningContainer}>
          <div className={`${styles.warning} ${isWarning ? styles.active : ""}`}>Press and Hold for 1 second</div>
        </div>

        {isHolding && <div className={styles.animate} />}
      </button>
      {disabled && <div className={styles.disabledBox} />}
    </div>
  );
}
