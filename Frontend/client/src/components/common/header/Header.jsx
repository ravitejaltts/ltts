import ArrowBackIosIcon from "@mui/icons-material/ArrowBackIos";
import React from "react";
import { useNavigate } from "react-router-dom";
import styles from "./header.module.css";

const Header = ({ text, extra }) => {
  let location = useNavigate();

  return (
    <div className={styles.header}>
      {/* <Link to="/"> */}

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
      <div className={styles.text}>{extra && extra.text}</div>

      {/* </Link> */}
    </div>
  );
};

export default Header;
