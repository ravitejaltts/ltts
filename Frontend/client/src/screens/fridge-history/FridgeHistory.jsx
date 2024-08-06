import axios from "axios";
import moment from "moment-timezone";
import React, { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { BackIcon } from "../../assets/asset";
import HistoryItem from "../../components/Refrigerator/TemperatureHistory/HistoryItem";
import useLocalStorage from "../../hooks/useLocalStorage";
import { API_ENDPOINT } from "../../utils/api";
import styles from "./index.module.css";
import { refData } from "../refrigrator/constants";

const FridgeHistory = () => {
  const [data, setData] = useLocalStorage("refrigrator-data", null);
  const [date, setDate] = useState(moment());
  const navigate = useNavigate();

  useEffect(() => {
    axios
      .put(
        data?.controls?.refrigerator_current_history?.refrigerator_full_history
          ?.PRESS?.action?.href || API_ENDPOINT.REFRIDGERATOR_FULL_HISTORY,
        {
          date: date.format("YYYY-MM-DD"),
          applianceType: "refrigerator",
        }
      )
      .then((res) => {
        if (res?.data) {
          setData(res?.data);
        }
      });
    // setData(refData);
  }, [date]);

  const handleNextDate = () => {
    setDate((prev) => moment(prev).add(1, "days"));
  };
  const handlePreviousDate = () => {
    setDate((prev) => moment(prev).subtract(1, "days"));
  };
  console.log(moment().format("DD-MM-YYYY"), date.format("DD-MM-YYYY"));
  console.log(moment().diff(date, "days"));

  return (
    <div className={styles.container}>
      <div className={styles.backContainer} onClick={() => navigate(-1)}>
        <BackIcon />
        <p className={styles.backText}>Back</p>
      </div>
      <div className={styles.header}>
        <p className={styles.headingText}>Refrigerator History</p>
      </div>
      <div className={styles.fridgeDiv}>
        <div className={styles.fridgeHeader}>
          <button className={styles.navContainer} onClick={handlePreviousDate}>
            <BackIcon />
            <p className={styles.backText}>Previous</p>
          </button>
          <div className={styles.headingTextContainer}>
            <p className={styles.mainHeading}>{date.format("MMMM DD")}</p>
            <p className={styles.today}>
              {date.format("YYYY-MM-DD") === moment().format("YYYY-MM-DD")
                ? "Today"
                : date.format("dddd")}
            </p>
          </div>
          <button
            className={`${styles.navContainer} ${styles.nextBtn}`}
            disabled={moment().diff(date, "days") < 1}
            onClick={handleNextDate}
          >
            <p className={styles.backText}>Next</p>

            <BackIcon />
          </button>
        </div>
        <div className={styles.contentContainer}>
          {data?.controls?.fullhistory?.data?.map((item, ind) => (
            <HistoryItem data={item} ind={ind} length={data?.data?.length} />
          ))}
        </div>
      </div>
    </div>
  );
};

export default FridgeHistory;
