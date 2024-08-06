import axios from "axios";
import React, { useContext, useEffect, useState } from "react";
import { Close } from "../../../assets/asset";
import Switch from "../../../components/common/switch/Switch";
import Brightness from "../../../components/lighting/brightness/Brightness";
import Rgb from "../../../components/lighting/rgb/Rgb";
import { DataContext } from "../../../context/DataContext";
import styles from "./rgbdimmer.module.css";

function MasterRgbAndDimmer({ handleClose, data, setRefetch, hideColorWheel }) {
  const { refreshParentData = () => {} } = useContext(DataContext);
  const [color, setColor] = useState();
  const [dataObj, setDataObj] = useState({
    rgb: color || data?.masterState?.rgb,
    brt: data?.masterState?.brt,
    onOff: data?.masterState?.onOff,
    clrTmp: data?.masterState?.clrTmp,
    // widget: data?.widget
  });

  const callAction = (payload) => {
    axios
      .put(
        data?.action_all?.action?.href,
        {
          ...payload,
        },
        {
          // timeout:1000
        },
      )
      .then(() => setRefetch(true));
  };

  useEffect(() => {
    setDataObj({
      rgb: color || data?.masterState?.rgb,
      brt: data?.masterState?.brt,
      onOff: data?.masterState?.onOff,
      clrTmp: data?.masterState?.clrTmp,
      widget: data?.widget,
      state: data?.state,
    });
  }, [data]);

  return (
    <div masteranddimmer="" className={styles.container}>
      <div className={styles.header}>
        <Close className={styles.closeIcon} onClick={handleClose} />
        <span className={styles.title}>{data?.title}</span>

        <Switch onOff={data?.state?.onOff} action={data?.action_all?.action} refreshParentData={refreshParentData} />
      </div>
      <div className={styles.content}>
        {data?.masterType === "RGBW" && !hideColorWheel && (
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

        <div className={styles.brightBox} style={{ width: data?.type === "SimpleDim" && "90%" }}>
          <Brightness data={dataObj} callAction={callAction} setRefetch={setRefetch} />
        </div>
      </div>
      {/* TODO: Add All On / All Off buttons here */}
    </div>
  );
}

export default MasterRgbAndDimmer;
