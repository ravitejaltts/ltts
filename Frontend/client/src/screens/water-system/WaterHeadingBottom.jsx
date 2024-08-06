import React from "react";
import screenStyles from "../../style/screen.css";
import System from "../../components/water-system/system/System";

function WaterHeadingBottom({ levels }) {
  const getClassName = (name) => {
    switch (name) {
      case "FreshTankLevel":
        return "pump-icon";
      case "GreyTankLevel":
        return "black-icon";
      case "BlackTankLevel":
        return "black-icon";
      default:
        return "blue-icon";
    }
  };

  return (
    <div className={`${screenStyles.headerBottomControls}`}>
      <div className="flex-row mt-auto grid-gap-4">
        {levels?.map((level, idx) => (
          <System key={idx} data={level} borderColor="var(--ui-elements-border2)" cls={getClassName(level.name)} />
        ))}
      </div>
    </div>
  );
}

export default WaterHeadingBottom;
