import React from "react";
import { useNavigate } from "react-router-dom";
import { BackIcon, FlashActive } from "../../../assets/asset";
import styles from "./index.module.css";

const time = [
  "12am",
  "2am",
  "4am",
  "6am",
  "8am",
  "10am",
  "12pm",
  "2pm",
  "4pm",
  "6pm",
  "8pm",
  "10pm",
];

const Meter = ({ level, ungrouped }) => {
  return (
    <div
      className={`${styles.meterDivContainer} ${
        ungrouped && styles.ungroupedMeter
      } ${level === "0%" && styles.emptyMeter}`}
    >
      <div className={`${styles.meterFill} `} style={{ height: level }}></div>
    </div>
  );
};

const MeterWrapperFlash = ({ children }) => {
  return (
    <div className={styles.meterWrapper}>
      <div className={styles.flashIcon}>
        <FlashActive />
      </div>
      {children}
    </div>
  );
};
const MeterWrapper = ({ children }) => {
  return <div className={styles.simpleWrapper}>{children}</div>;
};

const ChargeHistory = () => {
  const navigate = useNavigate();
  return (
    <div className={styles.container}>
      <div className={styles.backContainer} onClick={() => navigate(-1)}>
        <BackIcon />
        <p className={styles.backText}>Back</p>
      </div>
      <div className={styles.header}>
        <p className={styles.headingText}>Charge History</p>
      </div>
      <div className={styles.chargingDiv}>
        <div className={styles.chargingHeader}>
          <div className={styles.navContainer}>
            <BackIcon />
            <p className={styles.backText}>Previous</p>
          </div>
          <div className={styles.headingTextContainer}>
            <p className={styles.mainHeading}>May 31</p>
            <p className={styles.today}>Today</p>
          </div>
          <div className={`${styles.navContainer} ${styles.nextBtn}`}>
            <p className={styles.backText}>Next</p>

            <BackIcon />
          </div>
        </div>
        <div className={styles.meterContainer}>
          <div className={styles.scales}>
            <div>100%</div>
            <div>50%</div>
            <div>0%</div>
          </div>
          <div>
            <div className={styles.meterCollection}>
              <MeterWrapperFlash>
                <Meter level="7%" />
                <Meter level="15%" />
              </MeterWrapperFlash>
              <MeterWrapper>
                <Meter ungrouped level="7%" />
              </MeterWrapper>
              <MeterWrapper>
                <Meter ungrouped level="7" />
              </MeterWrapper>
              <MeterWrapper>
                <Meter ungrouped level="7" />
              </MeterWrapper>
              <MeterWrapperFlash>
                <Meter level="35%" />
              </MeterWrapperFlash>
              <MeterWrapper>
                <Meter ungrouped level="30%" />
              </MeterWrapper>
              <MeterWrapper>
                <Meter ungrouped level="30%" />
              </MeterWrapper>
              <MeterWrapper>
                <Meter ungrouped level="50%" />
              </MeterWrapper>
              <MeterWrapper>
                <Meter ungrouped level="70%" />
              </MeterWrapper>
              <MeterWrapper>
                <Meter ungrouped level="60%" />
              </MeterWrapper>
              <MeterWrapperFlash>
                <Meter level="70%" />
                <Meter level="95%" />
                <Meter level="90%" />
                <Meter level="88%" />
              </MeterWrapperFlash>
              <MeterWrapper>
                <Meter ungrouped level="0%" />
              </MeterWrapper>
              <MeterWrapper>
                <Meter ungrouped level="0%" />
              </MeterWrapper>
              <MeterWrapper>
                <Meter ungrouped level="0%" />
              </MeterWrapper>
              <MeterWrapper>
                <Meter ungrouped level="0%" />
              </MeterWrapper>
              <MeterWrapper>
                <Meter ungrouped level="0%" />
              </MeterWrapper>
              <MeterWrapper>
                <Meter ungrouped level="0%" />
              </MeterWrapper>
              <MeterWrapper>
                <Meter ungrouped level="0%" />
              </MeterWrapper>
              <MeterWrapper>
                <Meter ungrouped level="0%" />
              </MeterWrapper>
            </div>
            <div className={styles.timeContainer}>
              {time.map((item, ind) => (
                <div key={ind}>{item}</div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChargeHistory;
