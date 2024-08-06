import axios from "axios";

const baseURL = window?.location?.origin;

export const initAxios = () => {
  if (baseURL.includes("localhost")) {
    axios.defaults.baseURL = "http://127.0.0.1:8000/";
  } else {
    axios.defaults.baseURL = baseURL;
  }
};
