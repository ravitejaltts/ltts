import React, { useRef, useState } from "react";
import Keyboard from "react-simple-keyboard";
import "react-simple-keyboard/build/css/index.css";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";
import { Close } from "../../../assets/asset";
import styles from "./index.module.css";

export function JoinNetworkDialog({ close }) {
  const [input, setInput] = useState("");
  const [inputType, setInputType] = useState(true);
  const [layout, setLayout] = useState("default");
  const keyboard = useRef();

  const onChange = (input) => {
    setInput(input);
  };

  const toggleInputType = () => {
    setInputType((p) => !p);
  };
  const handleShift = () => {
    const newLayoutName = layout === "default" ? "shift" : "default";
    setLayout(newLayoutName);
  };

  const onKeyPress = (button) => {
    console.log("Button pressed", button);
    if (button === "{shift}" || button === "{lock}") handleShift();
  };

  const onChangeInput = (event) => {
    const input = event.target.value;
    setInput(input);
    keyboard.current.setInput(input);
  };
  const handleClick = () => {
    close();
  };

  return (
    <div className={styles.container}>
      <div className={styles.firstContainer}>
        <div className={styles.header}>
          <Close className={styles.closeBtn} onClick={close} />
          <p className={styles.headerText}>Join Network</p>
          <p className={`${styles.joinNowBtn} ${input && styles.active}`} onClick={handleClick}>
            Join Now
          </p>
        </div>
        <div>
          <p className={styles.passwordText}>PASSWORD</p>
          <div className={styles.inputBox}>
            <input
              className={styles.inputContainer}
              value={input}
              type={inputType ? "password" : "text"}
              placeholder={""}
              onChange={onChangeInput}
            />
            <div className={styles.icon} onClick={toggleInputType}>
              {inputType ? <VisibilityOffIcon /> : <VisibilityIcon />}
            </div>
          </div>
        </div>
      </div>

      <div className={styles.keyboard}>
        <Keyboard
          keyboardRef={(r) => (keyboard.current = r)}
          layoutName={layout}
          onChange={onChange}
          onKeyPress={onKeyPress}
        />
      </div>
    </div>
  );
}
