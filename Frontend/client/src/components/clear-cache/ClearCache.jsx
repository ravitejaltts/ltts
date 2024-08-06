import axios from "axios";
import { useEffect } from "react";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../utils/api";
import useLocalStorage from "../../hooks/useLocalStorage";

function ClearCache() {
  const [versionData, setVersionData] = useLocalStorage(LOCAL_ENDPOINT.VERSION_DATA, null);
  useEffect(() => {
    mountingCall();
  }, []);

  const mountingCall = async () => {
    let newVersionData;
    await axios.get(API_ENDPOINT.VERSION_DATA).then((res) => {
      newVersionData = res?.data?.date;
    });

    if (versionData !== newVersionData) {
      localStorage.clear();
    }
    setVersionData(newVersionData);
  };
  return null;
}

export default ClearCache;
