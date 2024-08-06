import axios from "axios";
import Slider from "rc-slider";
import "rc-slider/assets/index.css";
import { useContext } from "react";
import { BrightnessIcon } from "../../../../../assets/asset";
import { DataContext } from "../../../../../context/DataContext";
import styles from "./slider.module.css";

const BrightnessSlider = ({ data }) => {
  const { refreshParentData } = useContext(DataContext);
  const changeSliderValue = async (value) => {
    await axios
      .put(data?.action_default?.action?.href, {
        value,
      })
      .then((res) => {
        refreshParentData();
      })
      .catch((err) => {
        console.log(err);
      });

    console.log("ending");
  };
  return (
    <>
      <div className={`${styles.sliderContainer} flex align-center`}>
        <BrightnessIcon className={styles.brightnessIcon} />
        <div className={`${styles.slider}`}>
          <Slider
            min={data?.SimpleSlider?.min}
            max={data?.SimpleSlider?.max}
            value={data?.SimpleSlider?.value}
            step={data?.SimpleSlider?.step}
            style={{ color: "#4c85a9" }}
            onAfterChange={(e) => changeSliderValue(e)}
            onChange={(e) => changeSliderValue(e)}
          />
        </div>
        <BrightnessIcon className={styles.brightnessIcon} />
      </div>
      <p className={styles.borderBottom}></p>
    </>
  );
};

export default BrightnessSlider;
