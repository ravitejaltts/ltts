import { useEffect, useState } from "react";
import { DONT_CACHE } from "../utils/api";

export default function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    const data = localStorage.getItem(key);
    if (data === null || data === "undefined") {
      if (typeof initialValue === "function") {
        return initialValue();
      }
      return initialValue;
    }
    return JSON.parse(data);
  });

  useEffect(() => {
    if (value && !DONT_CACHE.includes(key)) {
      localStorage.setItem(key, JSON.stringify(value));
    }
  }, [value]);
  return [value, setValue];
}
