import React from 'react';
import styles from "./details.module.css"
import {BackIcon} from "../../../assets/asset"

const ActiveRow = () => <div className={styles.activeRow}>
<div className={styles.left}>
<div className={styles.iconBox}>
  <BackIcon />
</div>
<p>Thermostat</p>
</div>
  <div className={styles.right}>
    <p>4 hours ago</p>
    <p>400 W</p>
  </div>
</div>

const UsageDetails = () => {
  return (
    <div className={styles.details}>
      <div className={styles.row}>
        <h2>Active Systems</h2>
        <div className={styles.tabs}>
          <div className={styles.tab}>On Since</div>
          <div className={styles.tab}>Using</div>
        </div>
      </div>

      {/* bottom container */}
      <div className={styles.whiteContainer}>
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
        <ActiveRow />
      </div>
    </div>
  )
}

export default UsageDetails