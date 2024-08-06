import styles from "./diagnostics.module.css";

const LevelSlider = ({row}) => {

  return (
    <div className={`${styles.levelWidget}`}>
      <div className={`flex justify-between`}>
        <p>{row.title} ({row?.state?.level}%)</p>
        <p className={`subtext`}>{row.subtext}</p>
      </div>
      <div
        className={`${styles.levelWidgetSlider}`}
      >
        <div
          style={{
            width: `${row?.state?.level}%`,
          }}
          className={`${styles.levelWidgetSliderInner}`}
        ></div>
      </div>
    </div>
  );
};

export default LevelSlider;
