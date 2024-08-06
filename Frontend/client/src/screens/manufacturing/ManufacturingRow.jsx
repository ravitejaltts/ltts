import axios from "axios";
import styles from "./manufac.module.css";
import { SettingArrow } from "../../assets/asset";

function ManufacturingRow({ item, ind, showVinInput }) {
  const handleKeyboardToggle = (item) => {
    showVinInput(item);
  };

  const performAction = (actionObj) => {
    if (actionObj?.TAP?.actions?.href) {
      axios.put(actionObj?.TAP?.actions?.href);
    }
  };

  if (item?.type === "KeyboardEntry") {
    return (
      <div
        key={ind}
        onClick={() => handleKeyboardToggle(item)}
        className={`flex justify-between align-center ${styles.btnDiv}`}
      >
        <p>{item?.title}</p>
        <div className={styles.rightKeyboardDiv}>
          <p>{item?.state?.vin}</p>
          <SettingArrow className={styles.settingArrow} />
        </div>
      </div>
    );
  }
  if (item.type === "WIDGET_BUTTON") {
    return (
      <div key={ind} className={`flex justify-between align-center ${styles.btnDiv}`}>
        <p>{item?.title}</p>
        <button
          type="button"
          disabled={!(item?.enabled !== undefined || item.enabled)}
          onClick={() => performAction(item?.actions)}
        >
          {item?.text ? item?.text : "SEND"}
        </button>
      </div>
    );
  }
  if (item.type === "WIDGET_INFOLABEL") {
    return (
      <div key={ind} className={`flex justify-between align-center ${styles.btnDiv}`}>
        <p>{item?.title}</p>
        <div>
          <p>{item?.text}</p>
        </div>
      </div>
    );
  }
}

export default ManufacturingRow;
