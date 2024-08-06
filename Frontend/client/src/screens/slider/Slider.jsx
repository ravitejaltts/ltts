import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import twoImg from "../../assets/slides/2.png";
import threeImg from "../../assets/slides/3.png";
import fourImg from "../../assets/slides/4.png";
import fiveImg from "../../assets/slides/5.png";
import oneImg from "../../assets/slides/one.png";
import { getTimeDate } from "../../components/constants/helper";
import styles from "./slider.module.css";
// const imgArr = [
//   "https://media.geeksforgeeks.org/wp-content/uploads/20210208000010/1.png",
//   "https://media.geeksforgeeks.org/wp-content/uploads/20210208000009/2.png",
// ];
const imgArr = [oneImg, twoImg, threeImg, fourImg, fiveImg];

const Slider = () => {
  const navigate = useNavigate();
  const index = useRef(0);
  const [time, setTime] = useState();
  const [position, setPosition] = useState("");

  useEffect(() => {
    dataFetching();
    let timerId = setInterval(() => {
      dataFetching();
    }, 1000);

    let slideShowTimer = setInterval(() => {
      if (index.current === imgArr.length - 1) {
        return (index.current = 0);
      }
      index.current += 1;
    }, 30 * 1000);

    return () => {
      clearInterval(timerId);
      clearInterval(slideShowTimer);
    };
  }, []);

  const redirectBack = () => {
    navigate(-1);
    // navigate('/locked')
  };

  const dataFetching = () => {
    const data = getTimeDate();
    setTime(data);
  };

  return (
    <div
      className={styles.slider}
      onClick={redirectBack}
      onTouchStart={(e) => {
        setPosition(e.touches[0].screenY); //to set the point where swipe started
      }}
      onTouchEnd={(e) => {
        //if the difference between start and end point to sipe is greater teh 200px redirect back
        if (position - e.changedTouches[0].screenY >= 200) {
          setTimeout(() => {
            redirectBack();
          }, 500);
        }
      }}
    >
      <img className={styles.slide} src={imgArr[index.current]} alt="img" />
      <div className={styles.text}>
        <p className={styles.date}>
          {time?.[0]} {time?.[1]} {time?.[2]}
        </p>
        <p className={styles.time}>{time?.[4]}</p>
      </div>
    </div>
  );
};

export default Slider;
