import React, { useEffect, useState } from "react";
import styles from "./popup.module.css";

function Popup({ width, height, closePopup, top, children }) {
  const [topContainer, setTopContainer] = useState("100vh");
  const [topContent, setTopContent] = useState("100vh");
  const stopPropagation = (e) => e.stopPropagation();

  useEffect(() => {
    if (top !== "100vh") {
      setTopContainer("0");
      setTopContent(top);
    } else {
      setTimeout(() => {
        setTopContainer("100vh");
      }, 500);
    }
  }, [top]);

  const handleClose = () => {
    setTopContent("100vh");
    closePopup();
  };

  const childrenWithProps = React.Children.map(children, (child) => {
    if (React.isValidElement(child)) {
      return React.cloneElement(child);
    }
    return child;
  });

  return (
    <div id="Popup" className={styles.container} style={{ top: topContainer }} onClick={handleClose}>
      <div className={styles.content} style={{ width, height, top: topContent }} onClick={stopPropagation}>
        {childrenWithProps}
      </div>
    </div>
  );
}

export default Popup;
