import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import styles from "./ems.module.css";
import { FlashActive, FlashInactive, SettingArrow } from "../../assets/asset";
import { GeneratorPowerIcon } from "../../assets/assets";
import DeadmanButton from "../../components/common/deadman-button/DeadmanButton";

// Bottom card is practically the generator, but it should not be that hard coded
// TODO: Do a proper component per type as it comes in for power sources
function EmsBottomCard({ topText, bottomText, unit, onOff, name, ind, multiFuncSwitch, redirectTo, iconObj }) {
  const errorApiRef = useRef(false);
  const navigate = useNavigate();
  const handleHold = (actionObj) => {
    const val = actionObj?.action?.param.$mode;
    axios
      .put(actionObj?.action?.href, {
        mode: val,
      })
      .catch((err) => {
        if (err?.status === 423) {
          setDeadmanActive(null);
        }
      });
  };
  const [deadmanActive, setDeadmanActive] = useState(null);

  const handleRelease = (actionObj) => {
    if (actionObj) {
      errorApiRef.current = true;
      axios
        .put(actionObj?.action?.href, {
          ...actionObj?.action?.param,
        })
        .then(() => {
          errorApiRef.current = false;
        })
        .catch(() => {
          setTimeout(() => {
            handleRelease(actionObj);
          }, 1000);
        });
    }
  };

  return (
    <div
      key={ind}
      className="card p-4 mb-2 position-relative"
      onClick={redirectTo ? () => navigate(redirectTo) : undefined}
    >
      <div className={styles.arrowIcons}>
        <div className={styles.iconBox}>{onOff ? <FlashActive /> : <FlashInactive />}</div>
        {redirectTo && <SettingArrow />}
      </div>
      <div className={styles.cardTopRow}>
        {iconObj[name]}
        <p className={styles.cardTopText}>{topText}</p>
      </div>
      <div className={styles.cardBottom}>
        <p className={styles.cardBottomText}>
          {bottomText}
          <span className={styles.bottomText}>{unit}</span>
        </p>

        {multiFuncSwitch && (
          <div className={styles.multiFuncSwitchCont}>
            <DeadmanButton
              id={123}
              disabled={!multiFuncSwitch.enabled || errorApiRef.current}
              onReleaseCb={() => handleRelease(multiFuncSwitch.actions?.RELEASE)}
              longPressCallback={() => handleHold(multiFuncSwitch.actions?.HOLD)}
              holdDelayTime={multiFuncSwitch.holdDelayMs}
              apiCallIntervalTime={multiFuncSwitch.intervalMs}
              animateColor={multiFuncSwitch?.title === "Stop" ? "#f15f31" : "#55b966"}
              handleDeadman={setDeadmanActive}
              deadmanState={deadmanActive}
            >
              <div className={multiFuncSwitch?.title === "Stop" ? styles.multiFuncSwitchOff : styles.multiFuncSwitch}>
                <GeneratorPowerIcon />
                {multiFuncSwitch?.title}
              </div>
            </DeadmanButton>
          </div>
        )}
      </div>
    </div>
  );
}

export default EmsBottomCard;
