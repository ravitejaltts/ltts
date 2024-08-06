import React from "react";
import styles from "./generator.module.css";
import System from "../../components/water-system/system/System";
import { FlashActive, FlashInactive } from "../../assets/asset";

function GeneratorHeadingBottom({ data }) {
  return (
    <div className="headerBottomControls">
      <div className={styles.subTextContainer}>
        <div className={styles.iconBox}>
          {data?.overview?.powerStatus?.active ? <FlashActive /> : <FlashInactive />}
        </div>

        <p>
          <span className={styles.wattsValue}>{data?.overview?.powerStatus?.watts}</span>
          &nbsp; <span className={styles.subTxt}>{data?.overview?.powerStatus?.subtext}</span>
        </p>
      </div>

      <div className="flex-row mt-auto">
        {data?.overview?.levels?.map((level) => (
          <System key={level.name} data={level} borderColor="var(--ui-elements-border2)" classNames="propane-icon" />
        ))}
      </div>
    </div>
  );
}

export default GeneratorHeadingBottom;
