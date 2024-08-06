import React, { useState } from "react";
import styles from "./lock.module.css";

function LockScreenNumber(num) {
  const [code, setCode] = useState("");

  const handlePasscode = (num) => {
    setCode(code + num);
  };

  return (
    <div onClick={() => handlePasscode(num)} className={styles.numberCircle}>
      {num}
    </div>
  );
}

export default LockScreenNumber;
