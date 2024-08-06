import { useContext, useState } from "react";
import axios from "axios";
import {
  ArrowDownIcon,
  ArrowUpIcon,
  AwningDiagnosticIcon,
  ClimateControlIcon,
  CommunicationIcon,
  EnergyManagementIcon,
  LightsIcon,
  NeutralRoundIcon,
  SuccessRoundIcon,
  ToastPlaceholder,
  WarningRoundIcon,
  WaterSystemsIcon,
} from "../../../../assets/asset";
import styles from "./diagnostics.module.css";
import { AppContext } from "../../../../context/AppContext";

const SystemDiagnostics = ({ data }) => {
  console.log("data rec", data);
  const [expanded, setExpanded] = useState([]);

  const handleExpand = (name) => setExpanded([...expanded, name]);

  const handleCollapse = (name) => setExpanded(expanded?.filter((exp) => exp !== name));

  const handleFullExpand = () => {
    if (expanded.length === data?.categories?.length) setExpanded([]);
    else {
      const arr = [];
      data?.categories?.forEach((cat) => arr.push(cat?.title));
      setExpanded(arr);
    }
  };

  const appValues = useContext(AppContext);

  const handleRunDiagnostics = () => {
    axios.put(data?.top?.actions?.TAP?.api_call?.href);
  };

  return (
    <>
      <div className={styles.topContaienr}>
        <div className={styles.leftCont}>
          <p className={styles.checkTxt}>{data?.top?.text}</p>
          <p className={styles.lastranTxt}>{data?.top?.subtext}</p>
        </div>
        <div className={styles.rightBtn} onClick={handleRunDiagnostics}>
          {data?.top?.actions?.TAP?.title}
        </div>
      </div>

      <div className={styles.bottomContainer}>
        <div className={styles.row}>
          <p className={styles.resultsTxt}>{data?.middle?.left}</p>
          <p className={styles.link} onClick={handleFullExpand}>
            {expanded.length === data?.categories?.length ? "Collapse All Features" : "Expand All Features"}
          </p>
        </div>
        <div className={styles.bottomMainContainer}>
          {data?.categories?.map((category) => (
            <div className={styles.catCont}>
              <div className={styles.mainRow}>
                <div className={styles.rowLeft}>
                  {getIcon(category?.name)}
                  <p className={styles.categoryTitle}>{category?.title}</p>
                </div>
                <div className={`${styles.rowRight}`}>
                  {category?.status === "FAIL" ? <WarningRoundIcon /> : <SuccessRoundIcon />}
                  {expanded?.includes(category?.title) ? (
                    <ArrowUpIcon
                      onClick={() => handleCollapse(category?.title)}
                      className={`${appValues?.theme === "DARK" ? styles.darkicon : ""}`}
                    />
                  ) : (
                    <ArrowDownIcon
                      onClick={() => handleExpand(category?.title)}
                      className={`${appValues?.theme === "DARK" ? styles.darkicon : ""}`}
                    />
                  )}
                </div>
              </div>
              {expanded?.includes(category?.title) && (
                <div className={styles.expandedSection}>
                  {category?.devices?.map((device) => (
                    <div className={styles.innerRow}>
                      <div>
                        <div className={styles.innerTop}>
                          {device?.status === "FAIL" ? (
                            <WarningRoundIcon />
                          ) : device?.status === "PASS" ? (
                            <SuccessRoundIcon />
                          ) : (
                            <NeutralRoundIcon />
                          )}
                          <p className={styles.deviceStatus}>{device?.status}</p>
                        </div>
                        <div className={styles.innerMiddle}>{device?.title}</div>
                        <div className={styles.innerBottom}>{device?.text}</div>
                      </div>
                      {/* <DownArrowSmallIcon /> */}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </>
  );
};

export default SystemDiagnostics;


const getIcon = (name) => {
  switch (name) {
    case "AppFeatureEnergy":
     return <EnergyManagementIcon />
    case "AppFeatureWatersystems":
     return <WaterSystemsIcon />
    case "AppFeatureLighting":
      return <LightsIcon />
    case "AppFeatureElectrical":
      return <ToastPlaceholder className={styles.defaultIcon} />
    case "AppFeatureClimate":
      return <ClimateControlIcon />
    case "AppFeatureMovables":
      return <AwningDiagnosticIcon />
    case "AppFeatureGeneric":
      return <ToastPlaceholder className={styles.defaultIcon} />
    case "AppFeatureConnectivity":
      return <CommunicationIcon />
  }
}
