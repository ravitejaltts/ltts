import Header from "../../components/common/header/Header";
import Card from "../../components/levels/Card";
import styles from "./levels.module.css";
const levelsData = [
  {
    id: 1,
    heading: "Fresh Water",
  },
  {
    id: 2,
    heading: "Gray Water",
  },
  {
    id: 3,
    heading: "Battery",
  },
  {
    id: 4,
    heading: "Energy Usage",
  },
  // {
  //     id: 5,
  //     heading: 'Fresh Water'
  // },
];
const Levels = () => {
  return (
    <>
      <Header text="Levels" />
      <div className={styles.levels}>
        {levelsData.map(({ id, heading }) => (
          <Card key={id} heading={heading} />
        ))}
      </div>
    </>
  );
};

export default Levels;
