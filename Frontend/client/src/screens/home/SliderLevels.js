import {
  BlackTankLevel,
  FreshTankLevel,
  GreyTankLevel,
  HouseBatteryBgWhiteLevel,
  HouseBatteryLevel,
} from "../../assets/asset";
import { PropaneCylinerIcon } from "../../assets/assets";

import LevelWidget from "../../components/home/levelwidget/LevelWidget";

const iconObj = {
  HouseBatteryLevel: {
    icon: <HouseBatteryBgWhiteLevel />,
    cls: "inverter-icon",
  },
  PropaneTankLevel: {
    icon: <PropaneCylinerIcon />,
    cls: "propane-icon",
  },
  FreshTankLevel: { icon: <FreshTankLevel />, cls: "pump-icon" },
  GreyTankLevel: { icon: <GreyTankLevel />, cls: "black-icon" },
  BlackTankLevel: { icon: <BlackTankLevel />, cls: "black-icon" },
  default: {
    icon: <HouseBatteryLevel />,
    cls: "inverter-icon",
  },
};

export default function SliderLevels({ data }) {
  return (
    <>
      {data?.map((item, ind) => (
        <div key={ind}>
          <LevelWidget
            key={item.title}
            icon={iconObj?.[item?.name]?.icon || iconObj?.default?.icon}
            data={item}
            cls={iconObj?.[item?.name]?.cls || iconObj?.default?.cls}
            reRoute
          />
        </div>
      ))}
    </>
  );
}
