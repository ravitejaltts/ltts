import React, { useContext, useEffect, useState } from "react";
import { Outlet } from "react-router-dom";
import SideBar from "../SideBar";
import styles from "./layout.module.css";
import { DataContext } from "../../../context/DataContext";
import { AppContext } from "../../../context/AppContext";
import { useFetch } from "../../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../../utils/api";

function SettingLayout() {
  const { pollingInterval } = useContext(AppContext);
  const { data, refreshDataImmediate } = useFetch(API_ENDPOINT.SETTING, LOCAL_ENDPOINT.SETTING, true, pollingInterval);
  const [tabs, setTabs] = useState([]);
  const [activeTab, setActiveTab] = useState("");

  useEffect(() => {
    const tempTabs = [];
    // console.log('useefff',data)
    if (data) {
      data[0]?.tabs?.map((tab) => {
        if (tab?.details && Object.keys(tab?.details).length > 0) {
          tempTabs.push({
            title: tab.title,
            EOS: tab.EOS,
            name: tab.name,
          });
        }
      });
      setTabs(tempTabs);
    }
  }, [data]);

  return (
    <DataContext.Provider
      value={{
        refreshParentData: refreshDataImmediate,
      }}
    >
      <div className={styles.settingsContainer}>
        <div className={styles.left}>
          <SideBar tabs={tabs} active={activeTab} />
        </div>
        <div className={styles.right}>
          <Outlet context={[setActiveTab, data, refreshDataImmediate]} />
        </div>
      </div>
    </DataContext.Provider>
  );
}

export default SettingLayout;
