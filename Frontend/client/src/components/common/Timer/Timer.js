import { useIdleTimer } from "react-idle-timer";

export default function Timer({ timeout, setter }) {
  // const handleOnActive = () => setter(false);
  const handleOnIdle = () => setter(true);

  useIdleTimer({
    timeout,
    // onActive: handleOnActive,
    onIdle: handleOnIdle,
  });

  return null;
}
