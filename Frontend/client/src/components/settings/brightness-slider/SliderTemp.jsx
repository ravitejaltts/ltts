import axios from "axios";
import Slider from "rc-slider";
import "rc-slider/assets/index.css";
import { useContext, useEffect, useRef, useState } from "react";
import { PlusIcon, MinusIcon } from "../../../assets/asset";
import { DataContext } from "../../../context/DataContext";
import styles from "./slider.module.css";

const SliderTemp = ({ data }) => {
  const [value, setValue] = useState(data?.state?.brt || data?.state?.value);
  const isMountedRef = useRef(false);
  const { refreshParentData } = useContext(DataContext);
  const changeSliderValue = (val) => {
    setValue(val);
  };

  const apiCall = async () => {
    const payload = {}
    if(data?.state?.brt) {
      payload.brt = value
    }
    if(data?.state?.value) {
      payload.value = value
    }
    await axios
      .put(data?.action?.action?.href, payload)
      .then((res) => {
        refreshParentData();
      })
      .catch((err) => {
        console.log(err);
      });
  };
  useEffect(() => {
    if (isMountedRef.current) {
      const timer = setTimeout(() => {
        apiCall();
      }, 10);
      return () => clearTimeout(timer);
    } else {
      isMountedRef.current = true;
    }
  }, [value]);

  const handleBrightnessIncrease = () => setValue(value + data?.step);
  const handleBrightnessDecrease = () => setValue(value - data?.step);

  return (
    <>
      <div className={`${styles.sliderContainerTemp} flex align-center`}>
        <MinusIcon
          onClick={handleBrightnessDecrease}
          className={styles.brightnessIcon}
        />
        <div className={`${styles.slider}`}>
          <Slider
            min={data?.min}
            max={data?.max}
            value={value}
            step={data?.step}
            style={{ color: "#4c85a9" }}
            onAfterChange={(e) => changeSliderValue(e)}
            onChange={(e) => changeSliderValue(e)}
          />
        </div>
        <PlusIcon
          onClick={handleBrightnessIncrease}
          className={styles.brightnessIcon}
        />
      </div>
      <p className={styles.borderBottom}></p>
    </>
  );
};

export default SliderTemp;
