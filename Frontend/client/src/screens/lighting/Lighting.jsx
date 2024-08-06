import { useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppContext } from "../../context/AppContext";
import Popup from "../../components/common/Popup/Popup";
import LightingFeature from "./LightingFeature";
import { DataContext } from "../../context/DataContext";
import { useFetch } from "../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../utils/api";
import MasterRgbAndDimmer from "./rgbAndDimmer/MasterRgbAndDimmer";
import RgbAndDimmer from "./rgbAndDimmer/RgbAndDimmer";
import styles from "./lighting.module.css";
import LightingBodyHeading from "./LightingBodyHeading";
import LightingHeading from "./LightingHeading";
import LightingHeadingBottom from "./LightingHeadingBottom";

function Lighting() {
  const { pollingInterval, setSideBarShow } = useContext(AppContext);
  const [refetch, setRefetch] = useState(true);
  const { data, refreshDataImmediate } = useFetch(
    API_ENDPOINT.LIGHTING,
    LOCAL_ENDPOINT.LIGHTING,
    refetch,
    pollingInterval,
  );

  const [masterPopup, setMasterPopup] = useState(false);
  const navigate = useNavigate();
  const [popup, setPopup] = useState(false);
  const [popupData, setPopupData] = useState();

  useEffect(() => {
    if (data?.hideSidebar) {
      setSideBarShow(data?.hideSidebar);
    }
  }, [data]);

  const closePopup = useCallback(() => {
    setPopup(false);
  }, []);

  const openPopup = useCallback(() => {
    setPopup(true);
  }, []);

  const closeMasterPopup = () => {
    setMasterPopup(false);
  };

  const openSettingModal = () => {
    navigate(data?.overview.settings.href);
  };

  function getLights() {
    return data?.lights?.lights || [];
  }

  const refreshWrapperValue = useMemo(() => ({ refreshParentData: refreshDataImmediate }), [refreshDataImmediate]);

  return (
    <DataContext.Provider value={refreshWrapperValue}>
      <div id="Lighting" className="mainContainer">
        <div className="screenHeader">
          <LightingHeading title={data?.overview?.title} settings={openSettingModal} />
          <LightingHeadingBottom switches={data?.overview?.switches} />
        </div>

        <div className="screenBody">
          <div className="screenCard">
            <LightingBodyHeading
              data={data?.lights?.master}
              editAllLightsCallback={setMasterPopup}
              refreshDataImmediate={refreshDataImmediate}
            ></LightingBodyHeading>
            <div className="screenCardBody">
              <div className={styles.content}>
                {getLights().map((item, ind) => (
                  <LightingFeature
                    key={item?.title}
                    index={ind}
                    data={item}
                    closePopup={closePopup}
                    setPopupData={setPopupData}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {popup && data?.lights?.lights[popupData].type !== "SIMPLE_ONOFF" && (
        <Popup width="65%" height="100vh" top="0" closePopup={closePopup}>
          <RgbAndDimmer
            hideColorWheel={data?.lights?.lights[popupData]?.type !== "RGBW"}
            data={data?.lights?.lights[popupData]}
            togglePopup={closePopup}
            setRefetch={setRefetch}
          />
        </Popup>
      )}

      {masterPopup && (
        <Popup width="65%" height="100vh" top="0px" closePopup={closeMasterPopup}>
          <MasterRgbAndDimmer
            hideColorWheel={data?.master?.masterType !== "RGBW"}
            data={data?.lights?.master}
            handleClose={closeMasterPopup}
            setRefetch={setRefetch}
          />
        </Popup>
      )}
    </DataContext.Provider>
  );
}

export default Lighting;
