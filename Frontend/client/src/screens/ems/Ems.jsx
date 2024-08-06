import React, { useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { BackIcon, EmsBattery, EmsClimate, EmsHeater, EmsPro, EmsPump, EmsShore, EmsSolar } from "../../assets/asset";
import styles from "./ems.module.css";
import { AppContext } from "../../context/AppContext";
import { DataContext } from "../../context/DataContext";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../utils/api";
import { useFetch } from "../../hooks/useFetch";
import { EMSBolt } from "../../assets/assets";
import InverterWidget from "./inverter-widget/InverterWidget";
import EmsArrowTextCard from "./ems-arrow-text-card";
import EmsBottomCard from "./ems-bottom-card";
import EmsRightCard from "./ems-right-card";

const iconObj = {
  EmsSolarWidget: <EmsSolar />,
  EmsShoreWidget: <EmsShore />,
  EmsProPowerWidget: <EmsPro />,
  EmsUsageConsumerClimate: <EmsClimate />,
  EmsUsageConsumerWaterheater: <EmsHeater />,
  EmsUsageConsumerWaterPump: <EmsPump />,
};

function Ems() {
  const { pollingInterval, setSideBarShow } = useContext(AppContext);
  const { data, refreshDataImmediate } = useFetch(
    API_ENDPOINT.ENERGY_MANAGEMENT,
    LOCAL_ENDPOINT.ENERGY_MANAGEMENT,
    true,
    pollingInterval,
  );
  const navigate = useNavigate();

  useEffect(() => {
    if (data?.hideSidebar) {
      setSideBarShow(data?.hideSidebar);
    }
  }, [data]);

  if (!data) {
    return <div></div>;
  }

  // TODO: the older chrome 87 browser fails to render the page when useMemo is used for this page.
  // const refreshWrapperValue = useMemo(() => ({ refreshParentData: refreshDataImmediate }), [refreshDataImmediate]);

  return (
    // eslint-disable-next-line react/jsx-no-constructed-context-values
    <DataContext.Provider value={{ refreshParentData: refreshDataImmediate }}>
      <div className={styles.ems}>
        <div className={styles.header}>
          <div className={styles.backNav} onClick={() => navigate(-1)}>
            <BackIcon />
            <p className={styles.backText}>Back</p>
          </div>
          <p className={styles.energyText}>{data?.title}</p>
        </div>

        <div className={styles.mainContainer}>
          {!!data?.items[0]?.active && <div className={styles.greenBox1}></div>}
          {!!data?.items[1]?.active && <div className={styles.greenBox2}></div>}

          <div className={styles.contentWrapper}>
            <div className={styles.column}>
              <EmsArrowTextCard item={data?.items[0]} />
              {data?.items[0]?.widgets.map((widget, ind) => (
                <EmsBottomCard
                  key={ind}
                  topText={widget?.title}
                  bottomText={widget?.subtext}
                  unit={widget?.subtext_unit}
                  onOff={widget?.state?.onOff}
                  name={widget?.name}
                  ind={ind}
                  multiFuncSwitch={widget?.switches && widget?.switches[0]}
                  redirectTo={widget?.action_default?.action?.href}
                  iconObj
                />
              ))}
            </div>
            <div className={styles.column}>
              <EmsArrowTextCard item={data?.items[1]} />
              <div className="mb-2">
                <div className={`${styles.middleDiv}`}>
                  <div className={styles.batteryMainContainer}>
                    <div className={styles.batteryContainer}>
                      <EmsBattery />
                      {/* <p className={styles.innerBatteryText}>
                    {data?.items[1]?.widgets[0]?.BatteryMain?.value}
                    <span>%</span>
                  </p> */}
                      {/* <div
                    className={styles.innerBattery}
                    style={{
                      height: data?.items[1]?.widgets[0]?.BatteryMain?.value,
                    }}
                  ></div> */}
                      <div className={styles.innerBatteryColorFillContainer}>
                        <div
                          className={styles.innerBatteryColorFill}
                          style={{
                            height: `${data?.items[1]?.widgets[0]?.BatteryMain?.value}%`,
                          }}
                        ></div>
                        <EMSBolt className={styles.boltIcon} />
                      </div>
                    </div>
                    <div className={styles.batteryInfoContainer}>
                      <div
                        className={styles.batteryInfoDiv}
                        style={{
                          bottom: `${data?.items[1]?.widgets[0]?.BatteryMain?.value}% `,
                        }}
                      >
                        <div className={styles.leftArrow} />
                        <div>
                          <p className={styles.batteryInfoTitle}>{data?.items[1]?.widgets[0]?.BatteryMain?.toptext}</p>
                          <p className={styles.batteryInfoDivValue}>
                            {data?.items[1]?.widgets[0]?.BatteryMain?.value}
                            {data?.items[1]?.widgets[0]?.BatteryMain?.value_unit}
                            &nbsp; Charge
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className={styles.timeContainer}>
                  <div>
                    <span className={styles.remainingText}>
                      {data?.items[1]?.widgets[0]?.BatteryMain?.remaining_title}
                    </span>
                  </div>
                  <div>
                    <span className={styles.timeNum}>
                      {/* 00 */}
                      {data?.items[1]?.widgets[0]?.BatteryMain?.remaining_high}
                    </span>
                    <span className={styles.timeUnit}>
                      {/* Days */}
                      {data?.items[1]?.widgets[0]?.BatteryMain?.text_high}
                    </span>
                    <span className={styles.timeNum}>
                      {/* 00 */}
                      {data?.items[1]?.widgets[0]?.BatteryMain?.remaining_low}
                    </span>
                    <span className={styles.timeUnit}>
                      {/* hrs */}
                      {data?.items[1]?.widgets[0]?.BatteryMain?.text_low}
                    </span>
                  </div>
                </div>
              </div>

              {data?.items[1]?.widgets[1] && <InverterWidget data={data?.items[1]?.widgets[1]} />}
            </div>
            <div className={styles.column}>
              <div>
                <EmsArrowTextCard item={data?.items[2]} />
              </div>
              {!!data?.items[2]?.widgets[1]?.Consumers?.length && (
                <div className={`card p-4 ${styles.rightDiv}`}>
                  {/* <EmsUsage /> */}
                  {/* <div class={styles.ringContainer}>
                  <div class={styles.ring}></div>
                  <div
                    class={styles.ringOverlay}
                    style={{
                      transform: `rotate(${
                        Number(
                          (data?.items[2]?.widgets[0]?.UsageMain?.usage_level /
                            data?.items[2]?.widgets[0]?.UsageMain
                              ?.charge_level) *
                            180
                        ) + 45
                      }deg)`,
                    }}
                  ></div>
                  <div className={styles.whiteBar}></div>
                </div> */}
                  <div className={styles.rightCards}>
                    {data?.items[2]?.widgets[1]?.Consumers?.map((consumer, ind) =>
                      EmsRightCard(consumer?.title, consumer?.subtext, consumer?.name, ind, iconObj),
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </DataContext.Provider>
  );
}

export default Ems;
