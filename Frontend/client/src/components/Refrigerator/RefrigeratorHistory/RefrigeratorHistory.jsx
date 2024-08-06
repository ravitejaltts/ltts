import { useState } from "react";
import styles from "./history.module.css";
import HistoryItem from "../TemperatureHistory/HistoryItem";
import { REFRIDGERATOR_BUTTON_DEFAULT } from "../../../screens/refrigrator/constants";
import { useNavigate } from "react-router-dom";
import { HistoryIcon } from "../../../assets/asset";

const RefrigeratorHistory = ({ data }) => {
  const [selected, setSelected] = useState("Fridge");
  const navigate = useNavigate();
  return (
    <>
      <div className={styles.btnContainer}>
        <div
          className={`${styles.btn} ${
            selected === "Fridge" ? styles.activeBtn : ""
          }`}
          onClick={() => setSelected("Fridge")}
        >
          Fridge
        </div>
        <div
          className={`${styles.btn} ${
            selected === "Freezer" ? styles.activeBtn : ""
          }`}
          onClick={() => setSelected("Freezer")}
        >
          Freezer
        </div>
      </div>
      <div className={`${styles.belowTabsData}`}>
        {selected === "Fridge" && (
          <p className={`${styles.subtextText}`}>
            {data?.controls?.refrigerator_current_history?.subtext}
          </p>
        )}
        {selected === "Freezer" && (
          <p className={`${styles.subtextText}`}>
            {data?.controls?.freezer_current_history?.subtext}
          </p>
        )}

        <div className={styles.scrollableItems}>
          {selected === "Fridge" &&
            data?.controls?.refrigerator_current_history?.refrigerator_data?.map(
              (item, ind) => (
                <HistoryItem
                  key={ind}
                  data={item}
                  ind={ind}
                  length={data?.controls?.history?.data?.length}
                />
              )
            )}

          {selected === "Freezer" &&
            data?.controls?.freezer_current_history?.freezer_data?.map(
              (item, ind) => (
                <HistoryItem
                  key={ind}
                  data={item}
                  ind={ind}
                  length={data?.controls?.history?.data?.length}
                />
              )
            )}
        </div>

        <div
          onClick={() => {
            if (selected === "Fridge") {
              navigate("fridge-history");
            } else if (selected === "Freezer") {
              navigate("freezer-history");
            }
          }}
          className={styles.historyButton}
        >
          <HistoryIcon /> See {selected} History
        </div>
      </div>
    </>
  );
};

export default RefrigeratorHistory;
