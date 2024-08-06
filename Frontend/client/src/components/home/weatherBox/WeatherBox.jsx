import React from "react";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";

const WeatherBox = ({ data }) => {
  const styles = {};
  return (
    <>
      <p id="home-temp-text" style={{ opacity: 0.8 }}>
        {data?.header}
      </p>
      <p id="home-temp-desc-text" className={styles.weatherDesc}>
        {data?.content}
      </p>
      <div
        id="home-forecast-div"
        style={{ display: "flex", alignItems: "center" }}
      >
        <p id="home-forecast-text" style={{ margin: 0, fontSize: "40px" }}>
          {data?.footer}
        </p>{" "}
        <ArrowForwardIcon style={{ marginLeft: "10px", fontSize: "40px" }} />
      </div>
    </>
  );
};

export default WeatherBox;
