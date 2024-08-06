import React from "react";
import styles from "./modal.module.css";

const Modal = ({ setShowModal }) => {
  return (
    <div id="home-modal" className={styles.modal}>
      Lorem ipsum dolor, sit amet consectetur adipisicing elit. Cumque ea
      perferendis harum deleniti ut quidem quos dolorem quod ab modi eum
      recusandae corrupti est, illum eaque, sint suscipit accusamus dolores sit
      soluta voluptatibus. Ratione recusandae voluptates illo fugit obcaecati
      fuga nam beatae deleniti ex. Eius numquam sint quia incidunt tempora animi
      cum, atque debitis, nulla vero molestias illum laudantium iste fugiat. Cum
      debitis maiores labore quas molestias autem, mollitia commodi rem delectus
      saepe sit quia repudiandae dolor amet quasi et ipsum in quibusdam qui quo
      velit eligendi? Quasi obcaecati excepturi culpa officiis corporis,
      perferendis officia doloremque eveniet fugiat harum saepe vitae illum
      ratione adipisci deleniti possimus facere fugit. Commodi itaque beatae
      temporibus dolorum quidem ipsum exercitationem omnis atque cupiditate
      fugit doloremque molestias repudiandae culpa at iure sunt quae, nesciunt
      libero non nulla cumque ducimus delectus. Fugit nobis sapiente harum sed
      beatae atque nam, possimus voluptates fuga ab asperiores at, eum
      cupiditate nulla voluptate magnam ratione exercitationem quidem voluptas
      corporis praesentium itaque suscipit! Quidem facere voluptas eligendi at
      provident, beatae perspiciatis quos dignissimos officiis enim tempore
      maiores optio, voluptatibus, repellendus saepe. Sed quis delectus debitis
      quas sequi odio corrupti. A, possimus nesciunt ducimus sunt odit enim et
      beatae voluptas reprehenderit at!
      <button className={styles.btn} onClick={() => setShowModal(false)}>
        Close Modal
      </button>
    </div>
  );
};

export default Modal;
