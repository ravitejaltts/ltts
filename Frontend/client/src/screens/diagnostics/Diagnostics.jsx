import axios from "axios";
import React, { useContext, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../../context/AppContext";
import { BackIcon } from "../../assets/asset";
import SliderTemp from "../../components/settings/brightness-slider/SliderTemp";
import SettingRow from "../../components/settings/setting-row/SettingRow";
import { DataContext } from "../../context/DataContext";
import { useFetch } from "../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../utils/api";
import ls from "../../utils/helper/localStorage";
import styles from "./diagnostics.module.css";
import LevelSlider from "./LevelSlider";

const WidgetTypes = {
  WIDGET_TOGGLE: "WIDGET_TOGGLE",
  WIDGET_BUTTON: "WIDGET_BUTTON",
  WIDGET_LEVEL: "WIDGET_LEVEL",
  WIDGET_OPTIONS: "WIDGET_OPTIONS",
  WIDGET_SLIDER: "WIDGET_SLIDER",
  WIDGET_INFOLABEL: "WIDGET_INFOLABEL",
};

// TODO: This appears to be identical to FunctionalTest.jsx, except this isn't being used...

// Functional Test Panel
function Diagnostics() {
  // const sampleData = [
  //   { title: "All", swicthes: ["all switches here"] },
  //   { title: "Lighting", swicthes: ["lightning switches here"] },
  //   { title: "Climate", swicthes: [] },
  //   { title: "Water", swicthes: [] },
  //   { title: "Vehicle", swicthes: [] },
  //   { title: "Energy", swicthes: [] },
  //   { title: "Electrical", swicthes: [] },
  //   { title: "System", swicthes: [] },
  // ];
  const { pollingInterval, setSideBarShow } = useContext(AppContext);
  const [switchesData, setSwitchesData] = useState([]);
  const [category, setCategory] = useState(null);
  const { data, refreshDataImmediate } = useFetch(
    API_ENDPOINT.DIAGNOSTICS,
    LOCAL_ENDPOINT.DIAGNOSTICS,
    true,
    pollingInterval,
  );
  const [, setIdle] = useState(true);
  const navigate = useNavigate();
  // const { toggleRefresh } = useContext(AppContext);

  useEffect(() => {
    const result = ls.getItem("idleTimeout");
    if (!result) {
      return ls.setItem("idleTimeout", true);
    }
    if (result === "true") {
      setIdle(true);
    } else {
      setIdle(false);
    }
  }, []);

  useEffect(() => {
    const sampleData = data?.overview?.categories?.map((category) => {
      return {
        category,
        switches: category.category
          ? data.switches.filter((item) => item.category === category.category)
          : data.switches,
      };
    });
    setSwitchesData(sampleData || []);
  }, [data]);

  useEffect(() => {
    if (data?.hideSidebar) {
      setSideBarShow(data?.hideSidebar);
    }
  }, [data]);

  const doAction = (action) => {
    axios.put(action.href, action.params);
  };

  const doSelect = (action, optionParam, value) => {
    axios.put(action.href, { [optionParam]: value }).then(() => refreshDataImmediate());
  };

  const rowRenderer = (row, ind) => {
    if (row.type === WidgetTypes.WIDGET_TOGGLE) {
      return (
        <div className={styles.toggleDiv} key={ind}>
          <SettingRow
            name={row?.title}
            toggle
            text={row?.state?.onOff ? "On" : "Off"}
            toggleState={row?.state?.onOff}
            noBorder
            action={row?.action?.action}
            refreshDataImmediate={refreshDataImmediate}
          />
        </div>
      );
    }
    if (row.type === WidgetTypes.WIDGET_INFOLABEL) {
      return (
        <div className={styles.infoLabelDiv} key={ind}>
          <SettingRow name={row?.title} text={row?.text} noBorder bottomText={row?.subtext} />
        </div>
      );
    }
    if (row.type === WidgetTypes.WIDGET_SLIDER) {
      return (
        <div className={styles.sliderDiv} key={ind}>
          <div className="flex justify-between">
            <p>{row.title}</p>
            <p className="subtext">{row.subtext}</p>
          </div>
          <SliderTemp data={row} />
        </div>
      );
    }
    if (row.type === WidgetTypes.WIDGET_BUTTON) {
      return (
        <div className={`flex justify-between align-center ${styles.btnDiv}`} key={ind}>
          <p>{row.title}</p>
          <button type="button" onClick={() => doAction(row?.action?.action)}>
            {row.text ? row.text : "SEND"}
          </button>
        </div>
      );
    }
    if (row.type === WidgetTypes.WIDGET_OPTIONS) {
      return (
        <div className={`${styles.optionsWidget}`} key={ind}>
          <div className={`flex justify-between align-center ${styles.optionsTopDiv}`}>
            <div className={styles.centerTextDiv}>
              <h2 className={`${styles.lightMasterText}`}>{row?.title}</h2>
            </div>
            <p className={`${styles.lightsOnText}`}>{row?.subtext}</p>
          </div>
          <div className={`flex ${styles.options}`}>
            {row.options.map((option) => {
              const selected = row.state[row.option_param];

              return (
                <div
                  key={option.key}
                  className={`${styles.option} ${selected === option.value && styles.activeOption}`}
                  onClick={() => doSelect(row.action.action, row.option_param, option.value)}
                >
                  {option.key}
                </div>
              );
            })}
          </div>
        </div>
      );
    }
    if (row.type === WidgetTypes.WIDGET_LEVEL) {
      return <LevelSlider key={ind} row={row} />;
    }
  };

  const refreshWrapperValue = useMemo(() => ({ refreshParentData: refreshDataImmediate }), [refreshDataImmediate]);
  return (
    <DataContext.Provider value={refreshWrapperValue}>
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
          <h2 className={styles.waterHeadingText}>
            {data?.overview?.title?.split(" ")?.map((word, ind) => (
              <p className="m-0" key={ind}>
                {word}
              </p>
            ))}
          </h2>
          {/* </div> */}
          <div className={`${styles.categories}`}>
            {data?.overview?.categories?.map((categoryItem, ind) => (
              <div
                key={ind}
                onClick={() => setCategory(categoryItem.category)}
                className={`${styles.category} ${categoryItem.category === category && styles.activeBtn}`}
              >
                {categoryItem.title}
              </div>
            ))}
          </div>
        </div>
        {/* Right Div */}
        <div className={styles.rightDiv}>
          {category
            ? switchesData
                .filter((switchData) => switchData.category.category === category)
                .map((item, ind) => (
                  <React.Fragment key={ind}>
                    {item.switches.length > 0 && <h2 className="text-center">{item?.category.title}</h2>}

                    {item.switches.map((item, ind) => rowRenderer(item, ind))}
                  </React.Fragment>
                ))
            : switchesData
                .filter((switchData) => switchData.category.category != null)
                .map((item, ind) => (
                  <React.Fragment key={ind}>
                    {item.switches.length > 0 && <h2 className="text-center">{item?.category.title}</h2>}
                    {/* <h2 className="text-center">{item?.category.title}</h2> */}
                    {item.switches.map((item, ind) => rowRenderer(item, ind))}
                  </React.Fragment>
                ))}
        </div>
      </div>
    </DataContext.Provider>
  );
}

export default Diagnostics;
