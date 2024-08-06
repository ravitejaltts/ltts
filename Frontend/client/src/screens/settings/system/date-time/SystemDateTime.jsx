import React, { useEffect, useState } from "react";
import SettingRow from "../../../../components/settings/setting-row/SettingRow";
import styles from "./date.module.css";
import { SetDateDialog } from "../../../../components/settings/set-date-dialog/SetDateDialog";
import { SetTimeDialog } from "../../../../components/settings/set-time-dialog/SetTimeDialog";
import SystemTimezone from "../timezone/SystemTimezone";

const SystemDateTime = ({ data, innerSubpage, setInnerSubpage }) => {
  // const [subPage, setInnerSubpage] = useState(null);
  function close() {
    setInnerSubpage(null);
  }
  return (
    <>
      {!innerSubpage &&
        data?.data?.map((data, ind) => (
          <div className={styles.itemContainer} key={ind}>
            <p className={styles.containerHeading}>{data?.title}</p>
            <div className={styles.contentContainer}>
              {data?.data?.map((dat, ind, arr) => (
                <div key={ind}>
                  <SettingRow
                    name={dat?.title}
                    text={dat?.value}
                    toggle
                    toggleState={dat?.Simple?.onOff}
                    action={dat?.actions?.TOGGLE?.action}
                    noBorder={arr.length - 1 === ind}
                    bottomText={dat?.subtext}
                  />
                </div>
              ))}
              {data?.configuration?.map((dat, ind, arr) => (
                <div key={ind} onClick={() => setInnerSubpage(dat)}>
                  <SettingRow
                    name={dat?.title}
                    text={dat?.value || dat?.selected_text}
                    arrow={dat?.data}
                    toggleState={dat?.Simple?.onOff}
                    action={dat?.actions?.TOGGLE?.action}
                    noBorder={arr.length - 1 === ind}
                    bottomText={dat?.subtext}
                  />
                </div>
              ))}
            </div>
          </div>
        ))}
      {innerSubpage?.title === "Date" && (
        <SetDateDialog data={innerSubpage} close={close} />
      )}
      {innerSubpage?.title === "Time" && (
        <SetTimeDialog data={innerSubpage} close={close} />
      )}
      {innerSubpage?.title === "Timezone" && (
        // TODO: Make this update properly without hard coding array indices
        <SystemTimezone data={data?.data?.[0]?.configuration?.[0]} />
        // <SystemTimezone data={innerSubpage} />
      )}
    </>
  );
};

export default SystemDateTime;
