import {
  FreezerIcon,
  FridgeIcon,
  OutsideRangeIcon,
  WithinRangeIcon,
} from "../../../assets/asset";
import {
  REFRIDGERATOR_DEFAULT_TEMP,
  REFRIDGERATOR_SUB_TEXT,
  REFRIDGERATOR_TEMPERATURE_UNIT,
  REFRIDGERATOR_TOP_LINE,
} from "../../../screens/refrigrator/constants";
import styles from "./bottomTwo.module.css";

const LeftBottomTwoWidgets = ({ data }) => {
  const freezerData = data?.overview?.bottom_widget_freezer;
  const fridgeData = data?.overview?.bottom_widget_refrigerator;
  return (
    <div className={styles.leftBottomContainer}>
      <div className={styles.leftBottomDiv}>
        <div className={`flex`}>
          <FridgeIcon />
          <p className={styles.topText}>{fridgeData?.title || "Fridge"}</p>
        </div>
        <p
          className={styles.fText}
          style={{
            color: data?.overview?.bottom_widget?.alert && "#f7a300",
            fontWeight:
              data?.overview?.bottom_widget?.text === "--" ? "normal" : "bold",
          }}
        >
          {fridgeData?.text || REFRIDGERATOR_DEFAULT_TEMP}
          <span className={styles.fSmallText}>
            {fridgeData?.sidetext || REFRIDGERATOR_TEMPERATURE_UNIT}
          </span>
        </p>
        <p className={styles.currentText}>
          {data?.overview?.bottom_widget?.subtext || "Current Temp"}
        </p>

        {fridgeData?.subtext === "Inside Range" ? (
          <p
            className={`flex a-center ${styles.rangeText} ${styles.insideText}`}
          >
            <WithinRangeIcon /> {fridgeData?.subtext}
          </p>
        ) : (
          <p
            className={`flex a-center ${styles.rangeText} ${styles.outsideText}`}
          >
            <OutsideRangeIcon /> {fridgeData?.subtext}
          </p>
        )}
      </div>

      {/* niche */}
      <div className={styles.leftBottomDiv}>
        <div className={`flex`}>
          <FreezerIcon />
          <p className={styles.topText}>{freezerData?.title || "Fridge"}</p>
        </div>
        <p
          className={styles.fText}
          style={{
            color: data?.overview?.bottom_widget?.alert && "#f7a300",
            fontWeight:
              data?.overview?.bottom_widget?.text === "--" ? "normal" : "bold",
          }}
        >
          {freezerData?.text || REFRIDGERATOR_DEFAULT_TEMP}
          <span className={styles.fSmallText}>
            {freezerData?.sidetext || REFRIDGERATOR_TEMPERATURE_UNIT}
          </span>
        </p>
        <p className={styles.currentText}>
          {data?.overview?.bottom_widget?.subtext || "Current Temp"}
        </p>

        {freezerData?.subtext === "Inside Range" ? (
          <p
            className={`flex a-center ${styles.rangeText} ${styles.insideText}`}
          >
            <WithinRangeIcon /> {freezerData?.subtext}
          </p>
        ) : (
          <p
            className={`flex a-center ${styles.rangeText} ${styles.outsideText}`}
          >
            <OutsideRangeIcon /> {freezerData?.subtext}
          </p>
        )}
      </div>
    </div>
  );
};

export default LeftBottomTwoWidgets;
