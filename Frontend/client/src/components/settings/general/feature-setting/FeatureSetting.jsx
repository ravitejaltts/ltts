import React from "react";
import { useNavigate } from "react-router-dom";
import {
  BackIcon,
  ClimateThumbnail,
  EnergyThumbnail,
  LightsThumbnail,
  RefridgeratorThumbnail,
  WaterSystemsThumbnail,
} from "../../../../assets/asset";
import DetailRow from "../../../common/detail-row/DetailRow";
import styles from "./index.module.css";

const FeatureSettings = ({ setInnerFeatures, data }) => {
  const navigate = useNavigate();
  // const navigateTo = (url) => navigate(url);
  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.back} onClick={() => navigate(-1)}>
          <BackIcon />
          <h2>Back</h2>
        </div>
        <h2 className={styles.mainTitle}>{data?.title}</h2>
      </div>
      <div className={styles.infoContainer}>
        <div
          onClick={() => {
            // navigate("/settings/feature-settings-inner")
            setInnerFeatures(true);
          }}
        >
          <DetailRow
            icon={<ClimateThumbnail />}
            name="Climate Control"
            arrow
          />
        </div>
        <div>
          <DetailRow
            icon={<LightsThumbnail />}
            name="Lights"
            arrow
          />
        </div>
        <div>
          <DetailRow
            icon={<WaterSystemsThumbnail />}
            name="Water Systems"
            arrow
          />
        </div>
        <div>
          <DetailRow
            icon={<EnergyThumbnail />}
            name="Energy Management"
            arrow
          />
        </div>
        <div>
          <DetailRow
            icon={<RefridgeratorThumbnail />}
            name="Refrigerator"
            arrow
          />
        </div>
      </div>
    </div>
  );
};

export default FeatureSettings;
