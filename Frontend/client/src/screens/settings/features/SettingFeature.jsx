import React, { useContext, useEffect } from "react";
import { useLocation, useNavigate, useOutletContext } from "react-router-dom";
import { AppContext } from "../../../context/AppContext";
import {
  ClimateThumbnail,
  EnergyThumbnail,
  InverterThumbnail,
  LightsThumbnail,
  PetMonitorThumbnail,
  RefridgeratorThumbnail,
  WaterSystemsThumbnail,
} from "../../../assets/asset";
import DetailRow from "../../../components/settings/detail-row/DetailRow";
import { SETTINGS_LINKS } from "../../../constants/CONST";
import { useFetch } from "../../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../../utils/api";
import styles from "./feature.module.css";

const SettingFeature = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [setActiveTab, , refreshDataImmediate] = useOutletContext();
  const { pollingInterval } = useContext(AppContext);
  useEffect(() => {
    setActiveTab(location?.pathname);
  }, []);
  const { data } = useFetch(
    API_ENDPOINT.SETTING,
    LOCAL_ENDPOINT.SETTING,
    true,
    pollingInterval
  );

  const iconObj = {
    UiSettingsFeaturesDetailsClimate: <ClimateThumbnail />,
    UiSettingsFeaturesDetailsEnergy: <EnergyThumbnail />,
    UiSettingsFeaturesDetailsInverter: <InverterThumbnail />,
    UiSettingsFeaturesDetailsLights: <LightsThumbnail />,
    UiSettingsFeaturesDetailsPetMonitor: <PetMonitorThumbnail />,
    UiSettingsFeaturesDetailsRefrigerator: <RefridgeratorThumbnail />,
    UiSettingsFeaturesDetailsWaterSystems: <WaterSystemsThumbnail />,
  };

  const featureData = data?.[0]?.tabs?.filter(
    (tab) => `${tab.name}` === SETTINGS_LINKS.FEATURES
    )[0];

  return (
    <>
      <div className={styles.header}>
        <p className={styles.headingText}>{featureData?.title}</p>
      </div>

      <div className={styles.itemContainer}>
        <div className={styles.contentContainer}>
          {featureData?.details?.configuration?.map((dat, item, arr) => (
            <div key={dat?.name} onClick={() => navigate(`/setting/${dat?.name}`)}>
              <DetailRow icon={iconObj[dat?.name]} name={dat.title} arrow />
            </div>
          ))}
        </div>
      </div>
    </>
  );
};

export default SettingFeature;
