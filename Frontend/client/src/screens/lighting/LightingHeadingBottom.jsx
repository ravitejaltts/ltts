import React from "react";
import PresetSwitch from "../../components/lighting/preset/PresetSwitch";

function LightingHeadingBottom({ switches }) {
  return (
    <div className="flex-row mt-auto grid-gap-4">
      {switches?.map((item) => (
        <PresetSwitch key={item?.title} data={item} />
      ))}
    </div>
  );
}

export default LightingHeadingBottom;
