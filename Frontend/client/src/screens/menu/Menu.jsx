import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AutoScheduleIcon,
  AwningIcon,
  BatteryIcon,
  BatteryLevelsIcon,
  ClimateIcon,
  EnergyIcon,
  FlashActive,
  LivingRoomIcon,
  MenuBulbIcon,
  PetIcon,
  RefrigeratorIcon,
  SettingsIcon,
  SmartButtonIcon,
  WasteTanksIcon,
  WaterIcon,
} from "../../assets/asset";
import FeatureCard from "../../components/cards/FeatureCard";
import { getDataFromLocal } from "../../components/constants/helper";
import { useFetch } from "../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../utils/api";
import styles from "./menu.module.css";
import Header from "../../components/home/header/Header";

const iconObj = {
  AppFeatureLights: { icon: <MenuBulbIcon />, color: "lights-icon" },
  AppFeatureEms: { icon: <BatteryIcon />, color: "inverter-icon" },
  AppFeatureInverter: { icon: <EnergyIcon />, color: "inverter-icon" },
  AppFeatureRefrigerator: { icon: <RefrigeratorIcon />, color: "pump-icon" },
  AppFeatureWatersystems: { icon: <WaterIcon />, color: "pump-icon" },
  AppFeatureClimate: { icon: <ClimateIcon />, color: "heater-icon" },
  AppFeatureAwning: { icon: <AwningIcon />, color: "awning-icon" },
  AppAutomationSchedule: { icon: <AutoScheduleIcon />, color: "heater-icon" },
  AppAutomationSmartbuttons: {
    icon: <SmartButtonIcon />,
    color: "awning-icon",
  },
  AppReportBattLevels: { icon: <BatteryLevelsIcon />, color: "inverter-icon" },
  AppReportFreshLevels: { icon: <WaterIcon />, color: "pump-icon" },
  AppReportWasteLevels: { icon: <WasteTanksIcon />, color: "black-icon" },
  AppFeatureDebug: { icon: <SettingsIcon />, color: "pump-icon" },
  AppFeatureEngineeringPanel: { icon: <SettingsIcon />, color: "black-icon" },
  AppFeatureGeneratorPanel: { icon: <FlashActive />, color: "generator-icon" },
  AppFeatureSlideout: { icon: <LivingRoomIcon />, color: "slideout-icon" },
  AppFeaturePetMonitoring: { icon: <PetIcon />, color: "pet-monitor-icon" },
};

function Menu() {
  const { data: viewData } = useFetch(
    API_ENDPOINT.MENU,
    LOCAL_ENDPOINT.MENU,
    true
  );
  const { data: homeData } = useFetch(
    API_ENDPOINT.HOME,
    LOCAL_ENDPOINT.HOME,
    true
  );
  const [selected, setSelected] = useState(
    getDataFromLocal(LOCAL_ENDPOINT.MENU)?.[0]
  );
  const navigate = useNavigate();

  useEffect(() => {
    if (viewData) {
      setSelected(viewData[0]);
    }
  }, [viewData]);

  const navigateTo = (item) => {
    if (item?.action_default?.type === "navigate_external") {
      window.open(item.action_default.action.href, "_self");
    } else {
      navigate(item.action_default.action.href);
    }
  };

  return (
    <div className={styles.menuContainer}>
      {/* <div
        className={styles.homeIcon}
        onTouchEnd={(e) => {
          e.preventDefault();
          navigate(-1);
        }}
      >
        <HomeIcon />
      </div> */}
      {/* <div className={styles.topbar}> */}
      {/* <div className={styles.topbarBtns}>
        {viewData?.map((view, ind) => (
          <div
            className={`${styles.topBtn} ${
              view?.title === selected?.title && styles.selected
            }`}
            key={ind}
            onClick={() => setSelected(view)}
          >
            {view.title}
          </div>
        ))}
      </div> */}
      {/* <Test /> */}
      <div className={styles.topRow}>
        <Header data={homeData?.top} />
      </div>
      {selected?.title === "Features" && (
        <div className={styles.featuresContainer}>
          {selected?.items?.map((item) => (
            <FeatureCard
              heading={item.title}
              subHeading={item.subtext}
              color={iconObj[item.name]?.color || "inverter-icon"}
              icon={iconObj[item.name]?.icon || <SettingsIcon />}
              onClick={() => navigateTo(item)}
              topRightTitle={item?.toptext_title}
              topRightText={item?.toptext_subtext}
              key={item.name}
            />
          ))}
          {/* <FeatureCard
            heading={"Awning"}
            subHeading={"Awning subtext"}
            color={"lights-icon"}
            icon={<MenuBulbIcon />}
            onClick={() => navigate("/home/awning")}
            topRightTitle={""}
            topRightText={""}
            key={"awning"}
          />
          <FeatureCard
            heading={"Awning"}
            subHeading={"Awning subtext"}
            color={"lights-icon"}
            icon={<MenuBulbIcon />}
            onClick={() => navigate("/home/awning")}
            topRightTitle={""}
            topRightText={""}
            key={"awning"}
          />
          <FeatureCard
            heading={"Slide-Outs"}
            subHeading={"Slide-Outs subtext"}
            color={"lights-icon"}
            icon={<MenuBulbIcon />}
            onClick={() => navigate("/home/slide-outs")}
            topRightTitle={""}
            topRightText={""}
            key={"slide-out"}
          /> */}

          {/* <FeatureCard
            heading={"Inverter"}
            subHeading={""}
            color={"inverter-icon"}
            icon={<EnergyIcon />}
            onClick={() =>
              navigateTo({
                action_default: {
                  action: { href: "/home/inverter" },
                },
              })
            }
            height="232px"
            width="232px"
            key={"inverter"}
          /> */}
        </div>
      )}
      {selected?.title === "Automations" && (
        <div className={styles.autoContainer}>
          {selected?.items.map((item) => (
            <FeatureCard
              heading={item.title}
              subHeading={item.subtext}
              color={iconObj[item.name].color}
              icon={iconObj[item.name].icon}
              onClick={() => navigateTo(item)}
              key={item.name}
              height="472px"
              width="331px"
            />
          ))}
        </div>
      )}
      {selected?.title === "Reports" && (
        <div className={styles.autoContainer}>
          {selected?.items.map((item) => (
            <FeatureCard
              heading={item.title}
              subHeading={item.subtext}
              color={iconObj[item.name].color}
              icon={iconObj[item.name].icon}
              onClick={() => navigateTo(item)}
              key={item.name}
              height="472px"
              width="331px"
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default Menu;
