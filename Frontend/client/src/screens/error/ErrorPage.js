import { Navigate, useNavigate } from "react-router-dom";
import styles from "./error.module.css";

const ErrorPage = () => {
  const navigate = useNavigate()
  const goToHome = () => navigate('/')
  return (
    <div className={styles.container}>
      <h2>Error Occured</h2>
      <button onClick={goToHome}>Go To Home</button>
    </div>
  );
};

export default ErrorPage;
