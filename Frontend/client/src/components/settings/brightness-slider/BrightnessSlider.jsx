import axios from "axios";
import Slider from "rc-slider";
import "rc-slider/assets/index.css";
import { useContext, useEffect, useState } from "react";
import { BrightnessIcon } from "../../../assets/asset";
import { DataContext } from "../../../context/DataContext";
import styles from "./slider.module.css";

const BrightnessSlider = ({ data }) => {
  const [value, setValue] = useState(data?.SimpleSlider?.value);
  const { refreshParentData } = useContext(DataContext);
  const changeSliderValue = (val) => {
    console.log('Setting Slider Value: ' + val);
    if (val < (data?.SimpleSlider?.min || 10)) {
      return setValue(data?.SimpleSlider?.min || 10);
    }
    if (val > (data?.SimpleSlider?.max || 100)) {
      return setValue(data?.SimpleSlider?.max || 100);
    }
    setValue(val);
    apiCall(val);
  };

  const apiCall = async (value) => {
    console.log('Sending brightness API call')
    await axios
      .put(data?.actions?.SLIDE?.action.href, {
        value,
      })
      .then((res) => {
        refreshParentData();
      })
      .catch((err) => {
        console.log(err);
      });
  };

  // useEffect(() => {
  //   const timer = setTimeout(() => {
  //     apiCall();
  //   }, 10);
  //   return () => clearTimeout(timer);
  // }, [value, apiCall]);

  return (
    <>
      <div className={`${styles.sliderContainer} flex align-center`}>
        <BrightnessIcon
          className={styles.brightnessIcon1}
          onTouchStart={() =>
            changeSliderValue(value - data?.SimpleSlider?.step || 5)
          }
        />
        <div className={`${styles.slider}`}>
          <Slider
            min={data?.SimpleSlider?.min}
            max={data?.SimpleSlider?.max}
            value={value}
            step={data?.SimpleSlider?.step}
            trackStyle={{ backgroundColor: "#589cc6" }}
            onChange={(e) => changeSliderValue(e)}
          />
        </div>
        <BrightnessIcon
          className={styles.brightnessIcon2}
          onTouchStart={() =>
            changeSliderValue(value + data?.SimpleSlider?.step || 5)
          }
        />
      </div>
      <p className={styles.borderBottom}></p>
    </>
  );
};

export default BrightnessSlider;
