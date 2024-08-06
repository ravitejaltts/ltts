import React from "react";
import styles from "./ems.module.css";

function EmsArrowTextCard({ item }) {
  function getDisabledClass() {
    if (!item || !item.active) {
      return styles.disableColor;
    }
    return "";
  }

  return (
    <div className={`card p-4 mb-2 ${getDisabledClass()}`}>
      <p className={styles.topText}>{item?.title}</p>
      <p
        className={styles.bottomText}
        dangerouslySetInnerHTML={{
          __html: item?.subtext?.replace(
            `${item?.name === "EnergyBatteryColumn" ? "{soc}" : "{watts}"}`,
            `<span>${item?.name === "EnergyBatteryColumn" ? item?.state?.soc : item?.state?.watts}&nbsp;</span>`,
          ),
        }}
      ></p>
    </div>
  );
}

export default EmsArrowTextCard;
