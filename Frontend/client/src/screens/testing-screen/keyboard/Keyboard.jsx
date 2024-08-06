import React, { useState } from "react";
import { JoinNetworkDialog } from "../../../components/settings/join-network-dialog/JoinNetworkDialog";
import SettingRow from "../../../components/settings/setting-row/SettingRow";

const Keyboard = () => {
  const [displayInnerDetail, setDisplayInnerDetail] = useState(false);
  return (
    <>
      {!displayInnerDetail && (
        <div
          onClick={() => setDisplayInnerDetail(true)}
          style={{ backgroundColor: "var(--mode-bg-1)", borderRadius: "8px" }}
        >
          <SettingRow
            name={"Keyboard"}
            arrow
            noBorder={true}
            toggleState={false}
            action={null}
          />
        </div>
      )}
      {displayInnerDetail && (
        <JoinNetworkDialog close={() => setDisplayInnerDetail(false)} />
      )}
    </>
  );
};

export default Keyboard;
