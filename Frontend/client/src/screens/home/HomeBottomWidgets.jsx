import QuickActions from "./QuickActions";
import AutoMode from "./temp/AutoMode";
import CoolMode from "./temp/CoolMode";
import HeatMode from "./temp/HeatMode";
import FanMode from "./temp/FanMode";
import OffMode from "./temp/OffMode";
import SliderLevels from "./SliderLevels";
import styles from "./home.module.css";

export default function HomeBottomWidgets(inputs) {
  const { homeData, topValue } = inputs;
  return (
    <div style={{ top: `${topValue.current.toFixed(0)}px` }} id="HomeBottomWidgets">
      <div id="home-widgets" className={styles.widgets}>
        <div id="home-icon-box" className={styles.iconBox}>
          <QuickActions data={homeData?.quickactions} />
        </div>
        <div id="home-some-icon-box" className={styles.tempBox}>
          {homeData?.climateControlNew?.climateSystemMode === "AUTO" && <AutoMode data={homeData?.climateControlNew} />}
          {homeData?.climateControlNew?.climateSystemMode === "COOL" && <CoolMode data={homeData?.climateControlNew} />}
          {homeData?.climateControlNew?.climateSystemMode === "HEAT" && <HeatMode data={homeData?.climateControlNew} />}
          {homeData?.climateControlNew?.climateSystemMode === "FAN_ONLY" && (
            <FanMode data={homeData?.climateControlNew} />
          )}
          {homeData?.climateControlNew?.climateSystemMode === "OFF" && <OffMode data={homeData?.climateControlNew} />}
        </div>

        <div className={styles.homeLevels}>
          <SliderLevels data={homeData?.levels} />
        </div>
      </div>
    </div>
  );
}
