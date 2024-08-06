import React, { useContext } from "react";
import { DataContext } from "../../context/DataContext";
import Switch from "../../components/common/switch/Switch";
import styles from "./lighting-feature.module.css";

const LightingFeature = React.memo(({ data, closePopup, setPopupData, index }) => {
  const { refreshParentData = () => {} } = useContext(DataContext);
  const handlePopup = () => {
    setPopupData(index);
    closePopup();
  };
  const styleDisabled = () => {
    return data?.state.onOff === 0 ? styles.disable : "";
  };

  return (
    <div lightingfeature="" className="card m-1">
      <div className="cardHead">
        <div className="cardHeadStart m-4 me-0" onClick={data?.type !== "simple" ? handlePopup : undefined}>
          <h3 className={`cardTitle ${styleDisabled()}`}>{data?.title}</h3>
          <div className={styles.featureBottomContainer}>
            {data?.type === "RGBW" && (
              <p
                className={`${styles.circle} ${data?.state.onOff === 0 ? styles.disableBg : ""}`}
                style={{ background: data?.RGBW?.rgb }}
              ></p>
            )}
            <span
              className={`${styles.percentage} ${data?.subtext === "Off" && styles.disable} ${data?.type !== "RGBW" && "m-0"}`}
            >
              {data?.subtext}
            </span>
          </div>
        </div>
        <div className="cardHeadEnd m-4">
          <Switch
            onOff={data?.state.onOff}
            action={data?.action_default?.action}
            refreshParentData={refreshParentData}
          />
        </div>
      </div>
    </div>
  );
});

export default LightingFeature;
