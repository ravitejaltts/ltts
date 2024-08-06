import { useContext } from "react";
import { EmsInverterRotate } from "../../../assets/asset";
import Switch from "../../../components/common/switch/Switch";
import { numberFormat } from "../../../utils/utils";
import styles from "./inverter.module.css";
import { DataContext } from "../../../context/DataContext";

const InverterWidget = ({ data }) => {
  const { refreshParentData } = useContext(DataContext);
  const { load, maxLoad, onOff } = data?.state;
  var percentage = (load / maxLoad) * 100;
  var overload = false
  if (percentage > 100.0){
    // Limit to 100%
    percentage = 100
    overload = true
  }
  return (
    <div
      className={`${styles.inverterWidget} ${
        !data?.active && styles.disableColor
      }`}
    >
      <div className={styles.topDiv}>
        <div className={styles.iconAndTxt}>
          <EmsInverterRotate />
          <p className={styles.txt}>{data?.title}</p>
        </div>
        <Switch
          onOff={onOff}
          action={data?.action_default?.action}
          refreshParentData={refreshParentData}
        />
      </div>
      <div className={styles.progressBarCont}>
        <div className={styles.progressBar}></div>
        <div
          className={styles.selected}
          style={{
            width: `${percentage}%`,
            // backgroundColor: onOff ? "#55b966" : "#f7a300",
            backgroundColor: percentage === 100 ? "#FF0000" : percentage > 80 ? "#f7a300": "#55b966",
          }}
        ></div>
      </div>
      <div className={styles.loads}>
        <p
          className={styles.loadLeft}
          style={{ color: !overload ? percentage > 80 ? "#f7a300": "#55b966" : "#FF0000" }}
        >
          {numberFormat(load)} <span className={styles.unit}>W</span>
        </p>
        <p className={styles.loadRight}>
          of {maxLoad} <span className={styles.unit}>W</span>
        </p>
      </div>
    </div>
  );
};

export default InverterWidget;
