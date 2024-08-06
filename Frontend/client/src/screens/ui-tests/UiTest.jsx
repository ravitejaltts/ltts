import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { BackIcon } from "../../assets/asset";
import styles from "./ui.module.css";
import Keyboard from "../testing-screen/keyboard/Keyboard";

const WidgetTypes = {
  WIDGET_TOGGLE: "WIDGET_TOGGLE",
  WIDGET_BUTTON: "WIDGET_BUTTON",
  WIDGET_LEVEL: "WIDGET_LEVEL",
  WIDGET_OPTIONS: "WIDGET_OPTIONS",
  WIDGET_SLIDER: "WIDGET_SLIDER",
  WIDGET_INFOLABEL: "WIDGET_INFOLABEL",
};

const data = [
  {
    title: "Settings",
    child: [<Keyboard />],
  },
];

//Functional Test Panel
const UiTest = () => {
  const [category, setCategory] = useState(data[0].title);

  const navigate = useNavigate();

  return (
    <>
      {/* back navigation */}

      <div className={styles.mainContainer}>
        {/* Left Div */}
        <div className={styles.leftDiv}>
          {/* <div> */}
          <div className={styles.leftDivTop}>
            <div className={styles.backNav} onClick={() => navigate(-1)}>
              <div className={styles.backContainer}>
                <BackIcon />
              </div>
              <p className={styles.backText}>Back</p>
            </div>
          </div>
          <h2 className={styles.waterHeadingText}>UI Components</h2>
          {/* </div> */}
          <div className={`${styles.categories}`}>
            {data?.map((categoryItem) => (
              <div
                onClick={() => setCategory(categoryItem.title)}
                className={`${styles.category} ${
                  categoryItem.title === category && styles.activeBtn
                }`}
              >
                {categoryItem.title}
              </div>
            ))}
          </div>
        </div>
        {/* Right Div */}
        <div className={styles.rightDiv}>
          {category &&
            data
              ?.filter((switchData) => switchData.title == category)
              ?.map((item) => (
                <>
                  {item?.child.map((render) => (
                    <>{render}</>
                  ))}
                </>
              ))}
        </div>
      </div>
    </>
  );
};

export default UiTest;
