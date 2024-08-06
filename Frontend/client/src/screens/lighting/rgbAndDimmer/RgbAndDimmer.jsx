import axios from "axios";
import React, { useContext, useEffect, useState } from "react";
import { Close } from "../../../assets/asset";
import Switch from "../../../components/common/switch/Switch";
import Brightness from "../../../components/lighting/brightness/Brightness";
import Rgb from "../../../components/lighting/rgb/Rgb";
import { DataContext } from "../../../context/DataContext";
import styles from "./rgbdimmer.module.css";

function RgbAndDimmer({ handleClose, data, setRefetch, hideColorWheel }) {
  const { refreshParentData = () => {} } = useContext(DataContext);
  const [color, setColor] = useState();
  const [dataObj, setDataObj] = useState({
    rgb: data?.state?.rgb,
    brt: data?.state?.brt,
    onOff: data?.state?.onOff,
    clrTmp: data?.state?.clrTmp,
  });

  const callAction = (payload) => {
    axios
      .put(data?.action_default?.action?.href, {
        ...payload,
      })
      .then(() => setRefetch(true));
  };

  const getWidthStyle = () => {
    if (data?.type === "SimpleDim") {
      return { width: "90%" };
    }
  };

  useEffect(() => {
    setDataObj({
      rgb: color || data?.state?.rgb,
      brt: data?.state?.brt,
      onOff: data?.state?.onOff,
      clrTmp: data?.state?.clrTmp,
      widget: data?.widget,
      state: data?.state,
    });
  }, [data]);

  return (
    <div rgbanddimmer="" className={styles.container}>
      <div className={styles.header}>
        <Close className={styles.closeIcon} onClick={handleClose} />
        <span className={styles.title}>{data?.title}</span>

        <Switch
          onOff={data?.state?.onOff}
          action={data?.action_default?.action}
          refreshParentData={refreshParentData}
        />
      </div>
      <div className={styles.content}>
        {data?.type === "RGBW" && !hideColorWheel && (
          <div className={styles.colorBox}>
            <Rgb
              data={dataObj}
              setData={setDataObj}
              callAction={callAction}
              setRefetch={setRefetch}
              setColor={setColor}
              color={color}
            />
          </div>
        )}
        <div className={styles.brightBox} style={getWidthStyle()}>
          <Brightness data={dataObj} callAction={callAction} setRefetch={setRefetch} />
        </div>
      </div>
    </div>
  );
}

export default RgbAndDimmer;
