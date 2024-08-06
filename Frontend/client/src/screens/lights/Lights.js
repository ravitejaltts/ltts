import LeftCard from "../../components/climate-control/left-card/LeftCard";
import Header2 from "../../components/common/header2/Header2";
import SmallCard from "../../components/water-system/small-card/SmallCard";
import styles from "./lights.module.css";

const Lights = () => {
  return (
    <>
      <Header2 />
      <div className={styles.container}>
        <div className={styles.leftDiv}>
          <LeftCard />
        </div>

        <div className={styles.rightDiv}>
          <SmallCard />
          <SmallCard />
          <SmallCard />
          <SmallCard />
          <SmallCard />
          <SmallCard />
          <SmallCard />
          <SmallCard />
          <SmallCard />
          <SmallCard />
          <SmallCard />
          <SmallCard />
          <SmallCard />
          <SmallCard />
          <SmallCard />
          <SmallCard />
        </div>
      </div>
    </>
  );
};

export default Lights;
