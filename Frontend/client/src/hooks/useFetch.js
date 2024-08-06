import axios from "axios";
import { useEffect, useRef } from "react";
import useLocalStorage from "./useLocalStorage";

export function useFetch(url, key, refetch, pollingInterval = 5) {
  const [data, setData] = useLocalStorage(key, null);
  const refreshRate = useRef(pollingInterval);
  const timerRef = useRef(null);
  const mountedInstance = useRef(false);
  const controller = new AbortController();

  useEffect(() => {
    refreshRate.current = pollingInterval;
    if (mountedInstance.current) {
      dataFetching(refetch);
    }
    return () => {
      clearTimeout(timerRef.current);
      controller.abort();
    };
  }, [pollingInterval, refetch]);

  useEffect(() => {
    dataFetching(refetch);
    mountedInstance.current = true;
    return () => {
      controller.abort();
      mountedInstance.current = false;
      clearTimeout(timerRef.current);
    };
  }, []);

  const callDataFetching = () => {
    timerRef.current = setTimeout(() => {
      dataFetching(true);
    }, refreshRate.current * 1000);
  };

  const dataFetching = async (refetch) => {
    const result = await axios
      .get(url, { signal: controller.signal })
      .then((res) => {
        return res.data;
      })
      .catch((err) => {
        if (err?.message !== "canceled") {
          console.error("dataFetching error", err);
        }
        // setError(true);
      });

    if (mountedInstance.current) {
      if (result) {
        // setError(false);
        setData(result);
      }
      if (refetch) {
        callDataFetching();
      }
    }
  };

  const refreshDataImmediate = () => {
    dataFetching(false);
  };

  return { data, refreshDataImmediate };
}
