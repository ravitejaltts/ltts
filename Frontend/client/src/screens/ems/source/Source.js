import React from "react";
import { useNavigate } from "react-router-dom";
import {
  BackIcon,
  HookupIcon,
  PropulsionIcon,
  SolarIcon,
} from "../../../assets/asset";
import styles from "./source.module.css";

const SolarCard = () => {
  return (
    <div className={styles.solarCard}>
      <p className={styles.solarTopText}>Power</p>
      <h3 className={styles.solarMiddleText}>87</h3>
      <p className={styles.solarBottomText}>Watts</p>
    </div>
  );
};

const Source = () => {
  const navigate = useNavigate();
  return (
    <div className={styles.sourceContainer}>
      <div className={styles.backNav} onClick={() => navigate(-1)}>
        <BackIcon />
        <p className={styles.backText}>Back</p>
        <p className={styles.energyText}>Power Source</p>
      </div>

      {/* 1st row container */}

      <div className={styles.solarContainer}>
        <div className={styles.solarRow}>
          <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
            <div className={styles.iconBox}>
              <SolarIcon />
            </div>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                gap: "2px",
              }}
            >
              <h3 className={styles.topText}>Solar</h3>
              <p className={styles.bottomText}>
                Charge from 4 Victron Solar Pannels
              </p>
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center" }}>
            <div className={styles.iconBox}>
              <BackIcon />
            </div>
            <p className={styles.notChargingText}>Not Charging</p>
          </div>
        </div>
        <div className={styles.solarCardsContainer}>
          <SolarCard />
          <SolarCard />
          <SolarCard />
          <SolarCard />
          <div
            onClick={() => navigate("/sourceHistory")}
            className={styles.solarCard}
          >
            See history
          </div>
        </div>
      </div>

      {/* 2nd hook up */}

      <div className={styles.hookupContainer}>
        <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
          <div className={styles.iconBox}>
            <HookupIcon />
          </div>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "space-between",
              gap: "2px",
            }}
          >
            <h3 className={styles.topText}>Hook Up</h3>
            <p className={styles.bottomText}>
              Charge from shore hookup or Level 2 EV charger
            </p>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center" }}>
          <div className={styles.iconBox}>
            <BackIcon />
          </div>
          <p className={styles.notChargingText}>Not Charging</p>
        </div>
      </div>

      {/* 3rd propulsion container */}
      <div className={styles.propulsionContainer}>
        {/* copy from solar */}
        <div className={styles.solarRow}>
          <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
            <div className={styles.iconBox}>
              <PropulsionIcon />
            </div>
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                gap: "2px",
              }}
            >
              <h3 className={styles.topText}>Propulsion</h3>
              <p className={styles.bottomText}>
                Charge from your vehicles Propulsion Battery
              </p>
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center" }}>
            <div className={styles.iconBox}>
              <BackIcon />
            </div>
            <p className={styles.notChargingText}>Not Charging</p>
          </div>
        </div>
        <div className={styles.solarCardsContainer}>
          <SolarCard />
          <SolarCard />
          <SolarCard />
          <SolarCard />
        </div>
      </div>
    </div>
  );
};

export default Source;
