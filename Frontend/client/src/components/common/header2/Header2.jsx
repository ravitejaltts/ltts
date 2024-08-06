import ArrowBackIosIcon from "@mui/icons-material/ArrowBackIos";
import React from "react";
import { useNavigate } from "react-router-dom";
import styles from "./header2.module.css";

function Header2({ text }) {
  const location = useNavigate();

  return (
    <div className={styles.header}>
      <div>
        <ArrowBackIosIcon
          fontSize="large"
          onClick={() => {
            location(-1);
          }}
          style={{ cursor: "pointer" }}
        />
      </div>

      <div className={styles.text}>{text}</div>
    </div>
  );
}

export default Header2;
