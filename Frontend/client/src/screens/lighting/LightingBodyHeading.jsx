import React from "react";
import { BulbRightIcon } from "../../assets/asset";
import Switch from "../../components/common/switch/Switch";

function LightingBodyHeading({ data, editAllLightsCallback, refreshDataImmediate }) {
  return (
    <div lightingbodyheading="" className="largeCard" style={{ marginBottom: 0, borderRadius: 0 }}>
      <div className="cardHead p-4">
        <BulbRightIcon className="p-1" />
        <div className="cardHeadStart">
          <h2 className="cardTitle">{data?.title}</h2>
          <p className="cardSubTitle">{data?.subtext}</p>
        </div>
        <div className="cardHeadEnd">
          <button type="button" className="btnLink m-2" onClick={() => editAllLightsCallback(true)}>
            Edit All Lights
          </button>
        </div>
        <Switch
          onOff={data?.SIMPLE_ONOFF?.onOff}
          action={data?.action_default?.action}
          refreshParentData={refreshDataImmediate}
        />
      </div>
    </div>
  );
}

export default LightingBodyHeading;
