import React from "react";
import { GeneratorIcon } from "../../assets/assets";
import styles from "./generator.module.css";

function GeneratorHeading({ generatorsArray }) {
  const headingClass = `cardTitle ${
    (!generatorsArray[0].state.mode === 0 || generatorsArray[0]?.lockouts?.length > 0) && styles.disableText
  }`;
  const subHeadingClass = `cardSubTitle ${
    (!generatorsArray[0] || generatorsArray[0]?.lockouts?.length) && styles.disableText
  }`;

  return (
    <div className="largeCard" style={{ marginBottom: 0, borderRadius: 0 }}>
      <div className="cardHead p-4">
        <GeneratorIcon className={`${generatorsArray[0]?.active && styles.activeGenIcon} p-1 me-2`} />

        <div className="cardHeadStart">
          <h2 className={headingClass}>{generatorsArray[0]?.title}</h2>
          <p className={subHeadingClass}>{generatorsArray[0]?.subtext}</p>
        </div>
      </div>
    </div>
  );
}

export default GeneratorHeading;
