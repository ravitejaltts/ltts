import axios from "axios";
import React, { useRef } from "react";
import Button from "../common/Button/Button";
import styles from "./test.module.css";

const Test = () => {
  const ref = useRef(false);
  const timer = useRef(false);

  const callHoldApiCall = () => {
    ref.current = true;
    holdApiCall();
  };

  const holdApiCall = async () => {
    await axios
      .get("ui/notifications")
      .then((res) => {
        console.log("HOLD Api Call");
      })
      .finally(() => {
        if (ref.current) {
          timer.current = setTimeout(() => {
            holdApiCall();
          }, 100);
        }
      });
  };

  const UpApiCall = async () => {
    ref.current = false;
    clearTimeout(timer.current);
    await axios.get("ui/lighting/settings").then((res) => {
      console.log("Up Api Call");
    });
  };
  return (
    <>
      <div
        className={styles.testContainer}
        onTouchStart={callHoldApiCall}
        onTouchEnd={UpApiCall}
      >
        <Button text="Testing" />
      </div>
    </>
  );
};

export default Test;
