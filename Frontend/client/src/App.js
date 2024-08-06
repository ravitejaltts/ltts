import { useEffect, useMemo, useState } from "react";
import { Route, Routes } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import Timeout from "./components/common/Timeout/Timeout";
import { DARK_MODE, LIGHT_MODE } from "./components/constants/CONST";
import ChargeHistory from "./components/ems/ChargeHistory";
import NotFound404 from "./components/NotFound404";
import { SETTINGS_LINKS } from "./constants/CONST";
import "./style/global.css";
import "./style/screen.css";
import "./style/card.css";
import ClimateControl from "./screens/climate-control/ClimateControl";
import BatteryHistoryDetails from "./screens/ems/battery-history/BatteryHistoryDetails";
import Battery from "./screens/ems/battery/battery";
import Ems from "./screens/ems/Ems";
import Source from "./screens/ems/source/Source";
import SourceHistory from "./screens/ems/source/sourceHistory/SourceHistory";
import Usage from "./screens/ems/usage/Usage";
import ErrorPage from "./screens/error/ErrorPage";
import FunctionalTest from "./screens/functional-test/FunctionalTest";
import Home from "./screens/home/Home";
import Inverter from "./screens/inverter/Inverter";
import Lighting from "./screens/lighting/Lighting";
import LockScreen from "./screens/lock-screen/LockScreen";
import Menu from "./screens/menu/Menu";
import Refrigerator from "./screens/refrigrator/Refrigerator";
import SettingConnectivity from "./screens/settings/connectivity/SettingConnectivity";
import SettingDisplay from "./screens/settings/display/SettingDisplay";
import FeatureClimateControl from "./screens/settings/features/climate-control/FeatureClimateControl";
import FeatureEnergy from "./screens/settings/features/energy-management/FeatureEnergy";
import FeatureInverter from "./screens/settings/features/inverter/FeatureInverter";
import FeatureLights from "./screens/settings/features/lights/FeatureLights";
import FeaturePetMonitor from "./screens/settings/features/pet/FeaturePetMonitor";
import FeatureRefridgerator from "./screens/settings/features/refridgerator/FeatureRefridgerator";
import SettingFeature from "./screens/settings/features/SettingFeature";
import FeatureWater from "./screens/settings/features/water/FeatureWater";
import SettingNotification from "./screens/settings/notification/SettingNotification";
import SettingRevel from "./screens/settings/revel/SettingRevel";
import SettingSoftwareUpdate from "./screens/settings/software-update/SettingSoftwareUpdate";
import SettingSystem from "./screens/settings/system/SettingSystem";
import SettingUnitPreference from "./screens/settings/unit-preference/SettingUnitPreference";
import Slider from "./screens/slider/Slider";
import WaterSystem from "./screens/water-system/WaterSystem";
import ls from "./utils/helper/localStorage";
import removeContextMenu from "./utils/helper/removeContextMenu";
import SettingLayout from "./components/settings/setting-layout/SettingLayout";
import MainLayout from "./components/common/MainLayout/MainLayout";
import NotificationCenter from "./screens/notification-center/NotificationCenter";
import Awning from "./screens/awning/Awning";
import SlideOuts from "./screens/slide-outs/SlideOuts";
import UiTest from "./screens/ui-tests/UiTest";
import ClearCache from "./components/clear-cache/ClearCache";
import SlideOutsLegalDisclaimer from "./components/slide-outs/slide-outs-legal-disclaimer/SlideOutsLegalDisclaimer";
import Pairing from "./components/settings/pairing/Pairing";
import Generator from "./screens/generator/Generator";
import Manufacturing from "./screens/manufacturing/Manufacturing";
import FreezerHistory from "./screens/freezer-history/FreezerHistory";
import FridgeHistory from "./screens/fridge-history/FridgeHistory";
import Diagnostics from "./screens/diagnostics/Diagnostics";
import PetMonitoring from "./screens/pet-monitoring/PetMonitoring";
import * as AppContext from "./context/AppContext";

const AppContextProvider = AppContext.AppContext;

function App() {
  const [theme, setTheme] = useState(ls.getItem("theme") || "DARK");
  const [idle, setIdle] = useState(true);
  const [refresh, setRefresh] = useState(true);
  const [pollingInterval, setPollingInterval] = useState(1);
  const [animate, setAnimate] = useState(true);
  const [sideBarShow, setSideBarShow] = useState(true);
  useEffect(() => {
    localStorage.setItem("theme", LIGHT_MODE);
    window.addEventListener("contextmenu", (e) => {
      removeContextMenu(e);
    });
    localStorage.setItem("passcodeEntered", "false");
    return () => {
      window.removeEventListener("contextmenu", (e) => {
        removeContextMenu(e);
      });
    };
  }, []);

  const toggleRefresh = () => {
    setRefresh((prev) => !prev);
  };

  useEffect(() => {
    const result = ls.getItem("idleTimeout");
    setIdle(result !== "false");
  }, [refresh]);

  useEffect(() => {
    const clsDoc = document.body.classList;
    if (theme === DARK_MODE) {
      clsDoc.remove("light");
      localStorage.setItem("theme", DARK_MODE);
      return clsDoc.add("dark");
    }
    if (theme === LIGHT_MODE) {
      clsDoc.remove("dark");
      localStorage.setItem("theme", LIGHT_MODE);
      return clsDoc.add("light");
    }
    // changeMode();
  }, [theme]);

  const toggleTheme = (newTheme) => {
    if (newTheme) {
      return setTheme(newTheme);
    }
    setTheme((prev) => (prev === DARK_MODE ? LIGHT_MODE : DARK_MODE));
  };

  const refreshWrapperValue = useMemo(
    () => ({
      theme,
      setTheme,
      toggleTheme,
      toggleRefresh,
      pollingInterval,
      animate,
      setAnimate,
      sideBarShow,
      setSideBarShow,
    }),
    [],
  );

  return (
    <AppContextProvider.Provider value={refreshWrapperValue}>
      <ToastContainer
        className="toaster-container1"
        toastClassName="toast-className1"
        bodyClassName="toast-body1"
        position="bottom-center"
        autoClose={2000}
        hideProgressBar
        newestOnTop={false}
        rtl={false}
        closeButton={false}
        limit={1}
        draggable={false}
        closeOnClick={false}
        pauseOnHover={false}
        pauseOnFocusLoss={false}
      />
      <ClearCache />

      {idle && <Timeout setPollingInterval={setPollingInterval} />}
      <MainLayout>
        <Routes>
          {/* Home */}
          <Route path="/" element={<Home />} />
          <Route path="/locked" element={<LockScreen />} />
          <Route path="/error" element={<ErrorPage />} />
          {/* <Route path="/home" element={<Home />} /> */}
          <Route path="slider" element={<Slider />} />

          {/* Notification center */}
          <Route path="/notification-center" element={<NotificationCenter />} />

          {/* settings... */}
          {/* <Route path="settings/*" element={<Setting />} /> */}
          <Route path={SETTINGS_LINKS.LAYOUT} element={<SettingLayout />}>
            <Route path={SETTINGS_LINKS.REVEL} element={<SettingRevel />} />
            <Route path={SETTINGS_LINKS.CONNECTIVITY} element={<SettingConnectivity />} />
            <Route path={SETTINGS_LINKS.FEATURES} element={<SettingFeature />} />
            <Route path={SETTINGS_LINKS.NOTIFICATIONS} element={<SettingNotification />} />
            <Route path={SETTINGS_LINKS.UNIT_PREFERENCES} element={<SettingUnitPreference />} />

            {/* setting features sub pages */}
            <Route path={SETTINGS_LINKS.FEATURES_CLIMATE_CONTROL} element={<FeatureClimateControl />} />
            <Route path={SETTINGS_LINKS.FEATURES_ENERGY} element={<FeatureEnergy />} />
            <Route path={SETTINGS_LINKS.FEATURES_LIGHTS} element={<FeatureLights />} />
            <Route path={SETTINGS_LINKS.FEATURES_INVERTER} element={<FeatureInverter />} />
            <Route path={SETTINGS_LINKS.FEATURES_PET} element={<FeaturePetMonitor />} />
            <Route path={SETTINGS_LINKS.FEATURES_REFRIDGERATOR} element={<FeatureRefridgerator />} />
            <Route path={SETTINGS_LINKS.FEATURES_WATER} element={<FeatureWater />} />
            <Route path={SETTINGS_LINKS.SYSTEM} element={<SettingSystem />} />
            <Route path={SETTINGS_LINKS.SOFTWARE_UPDATE} element={<SettingSoftwareUpdate />} />
            <Route path={SETTINGS_LINKS.DISPLAY} element={<SettingDisplay />} />
            <Route path={SETTINGS_LINKS.CONNECTIVITY} element={<SettingConnectivity />} />
          </Route>

          <Route path="pairing" element={<Pairing />} />

          {/* App Menu */}
          <Route path="my-rv" element={<Menu />} />

          {/* Lighting screen */}
          <Route path="home/lighting" element={<Lighting />} />

          {/* Refrigerator screen */}
          <Route path="home/refrigerator" element={<Refrigerator />} />
          <Route path="home/refrigerator/fridge-history" element={<FridgeHistory />} />
          <Route path="home/refrigerator/freezer-history" element={<FreezerHistory />} />

          {/* ClimateControl screen */}
          <Route path="home/climatecontrol" element={<ClimateControl />} />
          <Route path="home/awning" element={<Awning />} />
          <Route path="home/slide-out-disclaimer" element={<SlideOutsLegalDisclaimer />} />
          <Route path="home/slide-outs" element={<SlideOuts />} />

          {/* FunctionalTest screen */}
          <Route path="home/functionaltests" element={<FunctionalTest />} />

          {/* Energy Management screen */}
          <Route path="home/ems" element={<Ems />} />
          <Route path="home/ems/Source" element={<Source />} />
          <Route path="home/ems/Battery" element={<Battery />} />
          <Route path="home/ems/Usage" element={<Usage />} />
          <Route path="home/ems/Battery/battery-history" element={<BatteryHistoryDetails />} />
          <Route path="home/ems/usage/history" element={<ChargeHistory />} />
          <Route path="sourceHistory" element={<SourceHistory />} />

          {/* WaterSystem screen */}
          <Route path="home/watersystems" element={<WaterSystem />} />

          {/* Inverter screen */}
          <Route path="home/inverter" element={<Inverter />} />

          {/* Pet Monitoring */}
          <Route path="/home/petmonitoring" element={<PetMonitoring />} />

          <Route path="home/uitests" element={<UiTest />} />
          <Route path="home/generator" element={<Generator />} />
          <Route path="home/manufacturing" element={<Manufacturing />} />
          <Route path="home/diagnostics" element={<Diagnostics />} />
          <Route path="home/:id" element={<NotFound404 />} />
          <Route path="*" element={<NotFound404 />} />
        </Routes>
      </MainLayout>
    </AppContextProvider.Provider>
  );
}

export default App;
