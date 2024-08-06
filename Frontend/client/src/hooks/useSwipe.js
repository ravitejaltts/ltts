import React, { useState } from "react";

const POSITION_DEFAULT_STATE = {
  xValue: null,
  yValue: null,
};

const useSwipe = (
  minDistance,
  leftSwipeCb = () => {},
  rightSwipeCb = () => {},
  downSwipeCb = () => {},
  upSwipeCb = () => {}
) => {
  const [touchStart, setTouchStart] = useState(POSITION_DEFAULT_STATE);
  const [touchEnd, setTouchEnd] = useState(POSITION_DEFAULT_STATE);

  const handleTouchStart = (e) => {
    setTouchEnd(POSITION_DEFAULT_STATE);
    setTouchStart({
      xValue: e.targetTouches[0].clientX,
      yValue: e.targetTouches[0].clientY,
    });
  };

  const handleTouchMove = (e) =>
    setTouchEnd({
      xValue: e.targetTouches[0].clientX,
      yValue: e.targetTouches[0].clientY,
    });

  const checkTouch = () => {
    if (
      typeof touchStart.xValue !== "number" ||
      typeof touchStart.yValue !== "number" ||
      typeof touchEnd.xValue !== "number" ||
      typeof touchEnd.yValue !== "number"
    ) {
      return true;
    }
    return false;
  };
  const handleTouchEnd = () => {
    if (checkTouch()) {
      return;
    }
    const horizontalDistance = touchStart.xValue - touchEnd.xValue;
    const verticalDistance = touchStart.yValue - touchEnd.yValue;
    const isLeftSwipe = horizontalDistance > minDistance;
    const isRightSwipe = horizontalDistance < -minDistance;
    const isUpSwipe = verticalDistance > minDistance;
    const isDownSwipe = verticalDistance < -minDistance;

    if (isLeftSwipe) {
      //   console.log("Left");
      return leftSwipeCb();
    }

    if (isRightSwipe) {
      //   console.log("Right");
      return rightSwipeCb();
    }
    if (isDownSwipe) {
      //   console.log("Down");
      return downSwipeCb();
    }
    if (isUpSwipe) {
      //   console.log("Up");
      return upSwipeCb();
    }
  };

  return [handleTouchStart, handleTouchMove, handleTouchEnd];
};

export default useSwipe;
