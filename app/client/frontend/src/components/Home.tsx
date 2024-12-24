import Navigator from './Navigator/Navigator';
import Footer from './Footer/Footer';
import Card from './Card';
import styles from "./home.module.css";

function Home() {
  const images = [
    "../../public/img/AI.png",
    "../../public/img/AI2.png",
    "../../public/img/AI3.png",
    "../../public/img/AI4.png",
    "../../public/img/AI5.png",
    "../../public/img/AI6.png",
    "../../public/img/AI7.png",
    "../../public/img/AI8.png",
  ];

  return (
    <>
      <div className={styles.home}>
        <Navigator />
        <div className={styles.content}>
          {images.map((image, index) => (
            <div className={styles.card} key={index}>
              <Card image={image} />  {/* 传递不同的图片 URL */}
            </div>
          ))}
        </div>
          <Footer/>
      </div>
    </>
  );
}

export default Home;
