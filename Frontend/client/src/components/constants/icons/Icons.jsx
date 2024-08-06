import {
  Awning,
  Fan,
  Heater,
  Inverter,
  Thermostat,
  WaterPump,
  Light,
} from "../../../assets/assets.jsx";
import styles from "./icon.module.css";

export const icons = {
  "Water Pump": <WaterPump className={styles.icon} />,

  Fire: <Thermostat className={styles.icon} />,

  "Water Heater": <Heater className={styles.icon} />,

  Fan: <Fan className={styles.icon} />,

  "Light Bulb": <Light className={styles.icon} />,

  "Awning Light": <Awning className={styles.icon} />,

  Inverter: <Inverter className={styles.icon} />,
};
