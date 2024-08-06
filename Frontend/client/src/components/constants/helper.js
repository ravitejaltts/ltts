import moment from "moment-timezone";
import { DARK_MODE } from "./CONST";
import { LOCAL_ENDPOINT } from "../../utils/api";

export const getTimeDate = () => {
  const homeSettings = getDataFromLocal(LOCAL_ENDPOINT.HOME_SETTINGS);
  const timeZone = homeSettings?.timezone;
  let newdate;
  if (moment.tz.zone(timeZone)) {
    newdate = moment(new Date()).tz(timeZone).format("ddd MMM D yyyy hh:mm A");
  } else {
    newdate = moment(new Date()).format("ddd MMM D yyyy hh:mm A");
  }
  const dates = newdate.split(" ");
  dates[4] = `${dates[4]} ${dates[5]}`;

  return dates;
};

export const getDataFromLocal = (string) => {
  return JSON.parse(localStorage.getItem(string));
};

export const setDataToLocal = (string, data) => {
  localStorage.setItem(string, JSON.stringify(data));
};

export const changeMode = () => {
  // to be improved further
  const clsDoc = document.body.classList;
  const homeSettingsData = getDataFromLocal("home-data");
  if (homeSettingsData?.settings?.screenMode === DARK_MODE) {
    clsDoc.remove("light");
    return clsDoc.add("dark");
  }
  clsDoc.remove("dark");
  return clsDoc.add("light");
};

export const compareProps = (prevProps, nextProps) => {
  return JSON.stringify(prevProps) === JSON.stringify(nextProps);
};
