import axios from "axios";
import styles from "./noti.module.css";

export default function PetNotification({ data, refreshDataImmediate }) {
  const action = (footer, type) => {
    if (!footer) return;
    try {
      const actionType = `action_${type}`;
      const path = `ui${footer[actionType].action.event_href}`;
      axios.get(path).finally(() => refreshDataImmediate());
    } catch (e) {
      console.log("error", e);
    }
  };

  const renderBody = (body) => {
    if (Array.isArray(body)) {
      return (
        <ul>
          {body?.map((text) => (
            <li>{text}</li>
          ))}
        </ul>
      );
    }
    return body;
  };
  return (
    <>
      <p className={styles.title}>{data?.title}</p>
      <div className={styles.subtile}>{data?.subtitle}</div>
      <div className={styles.body}>{renderBody(data?.body)}</div>
      <div className={styles.footer}>
        {data?.footer?.action?.map((btn, ind) => (
          <button type="button" className={styles.btn1} key={ind} onClick={() => action(data?.footer, btn)}>
            <span className={styles.btnText}>{btn?.text}</span>
          </button>
        ))}
      </div>
    </>
  );
}
