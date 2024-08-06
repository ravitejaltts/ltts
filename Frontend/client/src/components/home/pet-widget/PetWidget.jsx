import { useContext, useEffect } from "react";
import axios from "axios";
import { PetBackground, PetCritical, PetIcon, PetOK, PetWarning, WinnebagoLogo } from "../../../assets/asset";
import styles from "./pet.module.css";
import {
  BACKGROUND_PRIORITY,
  PET_SEVERITY_BG_COLOR,
  PET_SEVERITY_TYPE,
  PET_VAR_DEFAULT_COLOR,
} from "../../../constants/CONST";
import { MainContext } from "../../../context/MainContext";
import { DataContext } from "../../../context/DataContext";

export default function PetWidget({ data }) {
  const { setBgPriority } = useContext(MainContext);
  const { refreshParentData } = useContext(DataContext);

  useEffect(() => {
    if (data?.top?.state.enabled) {
      setBgPriority(BACKGROUND_PRIORITY.PET_MONITORING);
      switch (data?.status?.level) {
        case 0:
          document.body.style.background = PET_SEVERITY_BG_COLOR?.[PET_SEVERITY_TYPE.CRITICAL];
          break;
        case 1:
          document.body.style.background = PET_SEVERITY_BG_COLOR?.[PET_SEVERITY_TYPE.WARNING];
          break;

        case 4:
          document.body.style.background = PET_SEVERITY_BG_COLOR?.[PET_SEVERITY_TYPE.INFO];
          break;
        case 10:
          document.body.style.background = PET_SEVERITY_BG_COLOR?.[PET_SEVERITY_TYPE.DEFAULT];
          break;
        default:
      }
    } else {
      document.body.style.background = "";
      setBgPriority(BACKGROUND_PRIORITY.NOTIFICATION);
    }
    switch (data?.status?.level) {
      case 0:
        document.documentElement.style.setProperty(
          "--pet-color-mode",
          PET_VAR_DEFAULT_COLOR?.[PET_SEVERITY_TYPE.CRITICAL],
        );
        break;
      case 1:
        document.documentElement.style.setProperty(
          "--pet-color-mode",
          PET_VAR_DEFAULT_COLOR?.[PET_SEVERITY_TYPE.WARNING],
        );
        break;

      case 4:
        document.documentElement.style.setProperty("--pet-color-mode", PET_VAR_DEFAULT_COLOR?.[PET_SEVERITY_TYPE.INFO]);
        break;
      case 10:
        document.documentElement.style.setProperty(
          "--pet-color-mode",
          PET_VAR_DEFAULT_COLOR?.[PET_SEVERITY_TYPE.DEFAULT],
        );
        break;
      default:
        document.documentElement.style.setProperty("--pet-color-mode", "");
        break;
    }
  }, [data]);

  useEffect(() => {
    return () => {
      setBgPriority(BACKGROUND_PRIORITY.NOTIFICATION);
      document.documentElement.style.setProperty("--pet-color-mode", "var(--mode-text-inverse)");
    };
  }, []);

  const handleTap = () => {
    axios
      .put(data?.top?.actions?.TAP?.action?.href, {
        ...data?.top?.actions?.TAP?.action?.params,
      })
      .finally(() => {
        refreshParentData();
      });
  };

  const renderIcon = (level) => {
    switch (level) {
      case 0:
        return <PetCritical />;
      case 1:
        return <PetWarning />;
      case 4:
        return <PetWarning />;
      case 10:
        return <PetOK />;
      default:
        return <WinnebagoLogo className={styles.winnebagoLogo} />;
    }
  };
  return (
    <>
      <div className={styles.mainIcon}>{renderIcon(data?.status?.level)}</div>
      <div className={styles.container} onClick={handleTap}>
        <PetIcon />
        <span className={styles.text}>{data?.top?.title}</span>
      </div>
      {!!data?.top?.state?.enabled && (
        <div className={styles.backgroundImage}>
          <PetBackground />
        </div>
      )}
    </>
  );
}
