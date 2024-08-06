import styles from "./card.css";

const Card = ({ id, heading }) => {
  return (
    <div className={styles.card}>
      <div className={styles.cardData}>
        <h2>{heading}</h2>
        <h2>3 Days</h2>
        <button className={styles.historyBtn}>History</button>
      </div>
    </div>
  );
};

export default Card;
