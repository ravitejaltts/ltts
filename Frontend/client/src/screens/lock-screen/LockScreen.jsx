import axios from "axios";
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { API_ENDPOINT } from "../../utils/api";
import styles from "./lock.module.css";
import LockScreenNumber from "./LockScreenNumber";

function LockScreen() {
  const [code, setCode] = useState("");
  const [showToast, setShowToast] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (code.length === 8) {
      axios
        .put(API_ENDPOINT.LOCK_SCREEN, {
          passcode: parseInt(code, 10),
        })
        .then(() => {
          localStorage.setItem("passcodeEntered", "true");
          navigate("/");
        })
        .catch(() => {
          setShowToast(true);
          setCode("");
          console.log("validation fail");
        });
    }
  }, [code]);

  useEffect(() => {
    if (showToast) {
      setTimeout(() => {
        setShowToast(false);
      }, 1500);
    }
  }, [showToast]);

  const handleBack = () => {
    setCode(code.substring(0, code.length - 1));
  };

  return (
    <>
      {showToast && <div className={styles.invalid}>Invalid Passcode!!</div>}
      <p className={styles.entertext}>Enter Passcode</p>
      <div className={styles.container}>
        <div className={styles.dotContainer}>
          <div className={code.length >= 1 ? styles.dot : styles.emptyDot} />
          <div className={code.length >= 2 ? styles.dot : styles.emptyDot} />
          <div className={code.length >= 3 ? styles.dot : styles.emptyDot} />
          <div className={code.length >= 4 ? styles.dot : styles.emptyDot} />
          <div className={code.length >= 5 ? styles.dot : styles.emptyDot} />
          <div className={code.length >= 6 ? styles.dot : styles.emptyDot} />
          <div className={code.length >= 7 ? styles.dot : styles.emptyDot} />
          <div className={code.length >= 8 ? styles.dot : styles.emptyDot} />
        </div>
        <div className={styles.rowContainer}>
          <div className={styles.row}>
            {LockScreenNumber(1)}
            {LockScreenNumber(4)}
            {LockScreenNumber(7)}
            <button type="button" onClick={() => setCode("")} className="btnLink m-2">
              Reset
            </button>
          </div>
          <div className={styles.row}>
            {LockScreenNumber(2)}
            {LockScreenNumber(5)}
            {LockScreenNumber(8)}
            {LockScreenNumber(0)}
          </div>
          <div className={styles.row}>
            {LockScreenNumber(3)}
            {LockScreenNumber(6)}
            {LockScreenNumber(9)}
            <button type="button" onClick={handleBack} className="btnLink m-2">
              Back
            </button>
          </div>
        </div>
        {/* <div className={styles.row}>
          <p onClick={() => setCode('')}>Reset</p>
          {Number(0)}
          <p onClick={handleBack} className={styles.backText}>Back</p>
        </div> */}
      </div>
    </>
  );
}

export default LockScreen;
