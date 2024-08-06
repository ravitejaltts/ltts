import styles from "./heatFan.module.css";

const HeatSourceAndFan = ({ changeModal, tempBoxActive, thermostatData }) => {
  const activeHeatSource =
    thermostatData?.heatSource?.ToggleModal?.options?.filter(
      (item) => item?.selected === true
    )[0]?.key;
  const activFan = thermostatData?.acFanSpeed?.ToggleModal?.options?.filter(
    (item) => item?.selected === true
  )[0]?.key;
  return (
    <div
      className={`${styles.heatSourceAndFan} ${
        !tempBoxActive && styles.disable
      }`}
    >
      {thermostatData?.heatSource && (
        <div className={styles.item} onClick={() => changeModal("heat-modal")}>
          <p className={styles.text}>{thermostatData?.heatSource?.text}</p>
          <div className={styles.value}>{activeHeatSource}</div>
        </div>
      )}
      {thermostatData?.acFanSpeed && (
        <div className={styles.item} onClick={() => changeModal("fan-modal")}>
          <p className={styles.text}>{thermostatData?.acFanSpeed?.text}</p>
          <div className={styles.value}>{activFan}</div>
        </div>
      )}
    </div>
  );
};

export default HeatSourceAndFan;
