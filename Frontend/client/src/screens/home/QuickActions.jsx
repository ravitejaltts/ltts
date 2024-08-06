import { useContext } from "react";
import { ClimateBlackFanIcon, Inverter, Lights, WaterHeaterIcon, WaterPumpIcon } from "../../assets/asset";
import { DataContext } from "../../context/DataContext";
import ActiveWidget from "../../components/home/activeWidget/ActiveWidget";

const iconObj = {
  WaterPumpAction: { icon: <WaterPumpIcon />, color: "pump-icon" },
  WaterHeaterAction: { icon: <WaterHeaterIcon />, color: "heater-icon" },
  MasterLightAction: { icon: <Lights />, color: "lights-icon" },
  InverterAction: { icon: <Inverter />, color: "inverter-icon" },
  RoofFanAction: { icon: <ClimateBlackFanIcon />, color: "fan-icon" },
};

export default function QuickActions({ data }) {
  const { refreshParentData = () => {} } = useContext(DataContext);
  return (
    <>
      {data?.map((item) => (
        <div key={item.title}>
          <ActiveWidget
            data={item}
            icon={iconObj[item.name].icon}
            color={iconObj[item.name].color}
            refreshParentData={refreshParentData}
          />
        </div>
      ))}
      {data?.slice(0, 1).map((item) => (
        <div key={item.title}>
          <ActiveWidget
            data={item}
            icon={iconObj[item.name].icon}
            color={iconObj[item.name].color}
            refreshParentData={refreshParentData}
          />
        </div>
      ))}
    </>
  );
}
