import axios from "axios";
import React, { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { ActiveRoof, TempHot } from "../../../assets/asset";
import { DataContext } from "../../../utils/context/DataContext";
import styles from "./temp.module.css";

const Temp = ({ data }) => {
  const { refreshParentData = () => {} } = useContext(DataContext);
  const navigate = useNavigate();

  const redirect = () => {
    navigate(data?.action_default?.action?.href);
  };

  // const handleChange = async (e, change) => {
  //   e.stopPropagation();
  //   await axios
  //     .put(data?.decrease_temp?.action?.href, {
  //       $setTemp: data.setTemp + change,
  //     })
  //     .then((res) => {
  //       refreshParentData();
  //     });
  // };

  const activeFans = () => {
    return data?.fans.find((item) => item.active === 1);
  };

  return (
    <div id="com-temp" className={styles.container} onClick={redirect}>
      <div id="com-val" className={styles.mainTemp}>
        <span className={styles.iconBox}>
          <TempHot />
        </span>{" "}
        {data?.setTemp}
        <div
          className={`${activeFans() && styles.animationIcon} ${
            styles.fanIcon
          }`}
        >
          <ActiveRoof />
        </div>
      </div>
      <div id="com-indoor" className={styles.desc}>
        indoor {data?.internalTemp}
      </div>
      <div id="com-control" className={styles.controlBox}>
        <button
          id="com-btn"
          className={styles.controlButtons}
          // onClick={(e) => handleChange(e, -1)}

          // onTouchEnd={(e) => {e.stopPropagation()}}
        >
          -
        </button>
        <button
          id="com-btn1"
          className={styles.controlButtons}
          // onClick={(e) => handleChange(e, +1)}
          // onTouchEnd={(e) => {e.stopPropagation()}}
        >
          {" "}
          +
        </button>
      </div>
    </div>
  );
};

export default Temp;
