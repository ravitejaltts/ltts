import { useRef, useState } from "react";
import axios from "axios";
import { GeneratorPowerIcon } from "../../assets/assets";
import styles from "./generator.module.css";
import DeadmanButton from "../../components/common/deadman-button/DeadmanButton";

function GeneratorStop({ stopButtonData, generator }) {
  const [deadmanActive, setDeadmanActive] = useState(null);
  const errorApiRef = useRef(false);
  const powerButtonClass = `w-100 ${styles.powerBtn} ${generator?.state?.mode === 0 ? styles.stop : styles.start}`;

  if (!stopButtonData || !generator || Object.keys(generator).length === 0) {
    return <div></div>;
  }

  const handleHold = (actionObj) => {
    axios
      .put(actionObj?.action?.href, {
        ...actionObj?.action?.param,
      })
      .catch((err) => {
        if (err?.status === 423) {
          setDeadmanActive(null);
        }
      });
  };

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
    <div className="card p-3 m-auto" style={{ width: "300px" }}>
      <DeadmanButton
        disabled={!stopButtonData?.enabled || errorApiRef.current || (deadmanActive !== null && deadmanActive !== 1)}
        id={1}
        onReleaseCb={() => handleRelease(stopButtonData?.actions?.RELEASE)}
        longPressCallback={() => handleHold(stopButtonData?.actions?.HOLD)}
        holdDelayTime={stopButtonData?.holdDelayMs}
        apiCallIntervalTime={stopButtonData?.intervalMs}
        animateColor={stopButtonData?.title !== "Stop" ? "#55b966" : "#f15f31"}
        handleDeadman={setDeadmanActive}
        deadmanState={deadmanActive}
      >
        <div className={powerButtonClass}>
          <div className="d-inline-block text-center m-auto fw-bold">
            <GeneratorPowerIcon />
            <p>{stopButtonData?.title}</p>
          </div>
        </div>
      </DeadmanButton>
    </div>
  );
}

export default GeneratorStop;
