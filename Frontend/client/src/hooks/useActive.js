import { useEffect, useRef, useState } from "react";

const useActive = (time) => {
  const [active, setActive] = useState(true);
  const timer = useRef();
  const events = ["keypress", "mousemove", "touchmove", "click", "scroll"];
  useEffect(() => {
    const handelEvent = () => {
      setActive(true);
      if (timer.current) {
        window.clearTimeout(timer.current);
      }

      timer.current = window.setTimeout(() => {
        setActive(false);
      }, time);
    };

    document.body.addEventListener("click", () => {
      console.log("Clicked");
    });
    document.body.click();

    events.forEach((event) => document.addEventListener(event, handelEvent));

    return () => {
      events.forEach((event) => {
        document.removeEventListener(event, handelEvent);
      });
    };
  }, [time]);

  return active;
};

export default useActive;
