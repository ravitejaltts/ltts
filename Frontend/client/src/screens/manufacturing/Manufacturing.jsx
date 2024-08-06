import { useContext, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { AppContext } from "../../context/AppContext";
import { BackIcon } from "../../assets/asset";
import { DataContext } from "../../context/DataContext";
import { useFetch } from "../../hooks/useFetch";
import { API_ENDPOINT, LOCAL_ENDPOINT } from "../../utils/api";
import styles from "./manufac.module.css";
import { InputDialog } from "../../components/common/input-dialog/InputDialog";
import ManufacturingRow from "./ManufacturingRow";

function Manufacturing() {
  const { pollingInterval, setSideBarShow } = useContext(AppContext);
  const { data, refreshDataImmediate } = useFetch(
    API_ENDPOINT.MANUFACTURING,
    LOCAL_ENDPOINT.MANUFACTURING,
    true,
    pollingInterval,
  );
  const [inputDialog, setInputDialog] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (data?.hideSidebar) {
      setSideBarShow(data?.hideSidebar);
    }
  }, [data]);

  const handleKeyboardSubmit = (input) => {
    if (inputDialog?.actions?.ENTER?.actions?.href) {
      axios
        .put(inputDialog?.actions?.ENTER?.actions?.href, {
          vin: input,
        })
        .finally(() => {
          setInputDialog(null);
        });
    }
  };

  const showVinInput = (item) => {
    setInputDialog(item);
  };

  const refreshWrapperValue = useMemo(() => ({ refreshParentData: refreshDataImmediate }), [refreshDataImmediate]);

  return (
    <DataContext.Provider value={refreshWrapperValue}>
      {inputDialog && (
        <InputDialog title={inputDialog?.title} /* close={toggleInputModal} */ submitCb={handleKeyboardSubmit} />
      )}

      <div className={styles.mainContainer}>
        <div className={styles.leftDiv}>
          <div>
            <div className={styles.leftDivTop}>
              <div className={`${styles.backNav} ${data?.navigationLock && styles.hide}`} onClick={() => navigate(-1)}>
                <div className={styles.backContainer}>
                  <BackIcon />
                </div>
                <p className={styles.backText}>Back</p>
              </div>
            </div>
            <h2 className={styles.waterHeadingText}>
              {data?.overview?.title?.split(" ")?.map((word, ind) => (
                <p className="m-0" key={ind}>
                  {word}
                </p>
              ))}
            </h2>
          </div>
        </div>
        <div className={styles.rightDiv}>
          {data?.options?.map((item, ind) => (
            <ManufacturingRow item={item} key={ind} ind={ind} showVinInput={showVinInput} />
          ))}
        </div>
      </div>
    </DataContext.Provider>
  );
}

export default Manufacturing;
