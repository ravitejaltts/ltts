import React from "react";
import styles from "./bigcard.module.css";
import OpacityIcon from "@mui/icons-material/Opacity";
import SettingsIcon from "@mui/icons-material/Settings";
import { IconBoxCircle, IconBoxSquare } from "../../common/helper/Helper";
import Subcard from "../sub-card/Subcard";

const BigCard = ({ icon, icon2, text }) => {
  return (
    <div className={styles.card}>
      <div>
        <div className={styles.topRow}>
          <IconBoxSquare icon={<OpacityIcon className={styles.icon} />} />
          <IconBoxCircle icon={<SettingsIcon className={styles.icon2} />} />
        </div>
        <div className={styles.middleRow}>Water Systems</div>
      </div>
      <div className={styles.bottomRow}>
        <Subcard />
        <Subcard />
      </div>
    </div>
  );
};

export default BigCard;
