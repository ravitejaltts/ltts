import React, { useEffect, useState } from "react";
import styles from "./pairing.module.css";
import { Close } from "../../../assets/asset";
import PairingProgress from "./PairingProgress";
import PairingError from "./PairingError";
import PairingSuccess from "./PairingSuccess";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../../utils/api";
import axios from "axios";
import { useFetch } from "../../../hooks/useFetch";

const messages = [
  "Download the Winnebago App from the Android or Apple App Store",
  "Turn on your RV, and make sure it’s in park.",
  "In the App, create your account and when asked select “WinnConnect Enabled RV”",
  "When prompted, scan the QR code to the right.",
];
const Pairing = ({ close, data }) => {
  const [mode, setMode] = useState(null);
  const [qrBase64, setQrBase64] = useState(null);

  // useEffect(() => {
  //   axios.get(API_ENDPOINT.PAIRING_QR_CODE).then((res) => {
  //     console.log("resres", res);
  //     if (res?.data) {
  //       setQrBase64(res.data.qr_value);
  //       setMode(res.data.status);
  //     }
  //   });
  // });

  const { data: qrData, refreshDataImmediate } = useFetch(
    API_ENDPOINT.PAIRING_QR_CODE,
    LOCAL_ENDPOINT.SLIDE_OUT_SCREEN,
    true,
    1
  );

  useEffect(() => {
    console.log("qrData", qrData);
    if (qrData) {
      setQrBase64(qrData.qr_value);
      setMode(qrData.status);
    }
  }, [qrData]);

  return (
    <div className={styles.container}>
      <div className={styles.header} onClick={close}>
        <Close />
        <span>Cancel</span>
      </div>
      <div className={styles.mainContent}>
        {mode === 0 && (
          <div className={styles.content}>
            <div className={styles.left}>
              <p className={styles.msgHeader}>{data?.title}</p>
              <p className={styles.msgHeader2}>{data?.subtext}</p>
              {data?.data?.[0]?.data?.map((msg, ind) => (
                <div className={styles.instruction} key={ind}>
                  <p className={styles.number}>{msg?.numbered_item}</p>
                  <p className={styles.description}>{msg?.instruction}</p>
                </div>
              ))}
            </div>
            <div className={styles.right}>
              <div className={styles.qr}>
                <img
                  loading="lazy"
                  src={`data:image/jpeg;base64,${qrBase64}`}
                  height="342px"
                  width="342px"
                />
              </div>
              <p className={styles.qrHelper}>{data?.data?.[1]?.subtext}</p>

              <p className={styles.vNumber}> {data?.data?.[1]?.footer}</p>
            </div>
          </div>
        )}
        {mode === 1 && <PairingProgress />}
        {mode === 2 && <PairingSuccess close={close} />}
        {mode === 3 && <PairingError close={close} />}
      </div>
    </div>
  );
};

export default Pairing;
