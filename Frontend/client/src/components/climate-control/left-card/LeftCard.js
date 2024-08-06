import OpacityIcon from "@mui/icons-material/Opacity";
import SettingsIcon from "@mui/icons-material/Settings";
import { IconBoxCircle, IconBoxSquare } from "../../common/helper/Helper";
import styles from "./left.module.css";

const LeftCard = () => {
  return (
    <div className={styles.card}>
      <div>
        <div className={styles.topRow}>
          <IconBoxSquare icon={<OpacityIcon className={styles.icon} />} />
          <IconBoxCircle icon={<SettingsIcon className={styles.icon2} />} />
        </div>
        <div className={styles.middleRow}>Climate Control</div>
      </div>
      <div>
        <p className={styles.forecast}>Today's forecast</p>
        <hr />
        <div className={styles.belowLine}>
          <div className={styles.currentAndOutdoor}>
            <div className={styles.current}>
              <span>Current</span>
              <span>
                <OpacityIcon className={styles.icon} />
              </span>
            </div>
            <div className={styles.outdoor}>Outdoor Temp</div>
          </div>
          <div className={styles.temperature}>48°</div>
        </div>
      </div>
      <div className={styles.bottomRow}>
        <div className={styles.box}>
          <OpacityIcon className={styles.icon} />
          <div className={styles.boxData}>
            <div>48°</div>
            <div>Morning</div>
          </div>
        </div>
        <div className={styles.box}>
          <OpacityIcon className={styles.icon} />
          <div className={styles.boxData}>
            <div>48°</div>
            <div>Morning</div>
          </div>
        </div>
        <div className={styles.box}>
          <OpacityIcon className={styles.icon} />
          <div className={styles.boxData}>
            <div>48°</div>
            <div>Morning</div>
          </div>
        </div>
        <div className={styles.box}>
          <OpacityIcon className={styles.icon} />
          <div className={styles.boxData}>
            <div>48°</div>
            <div>Morning</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LeftCard;
