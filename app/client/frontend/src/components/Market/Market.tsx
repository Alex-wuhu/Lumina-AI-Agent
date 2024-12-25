import Navigator from '../Navigator/Navigator';
import Footer from '../Footer/Footer';
import Card from '../Card';
import React, { useState, useEffect, useRef } from "react";
import NET from "vanta/dist/vanta.net.min";
import styles from "./market.module.css";

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
  const [vantaEffect, setVantaEffect] = useState(null);
  const myRef = useRef(null);
  useEffect(() => {
    if (!vantaEffect) {
      setVantaEffect(
        NET({
          el: myRef.current,
          color: 0x1E90FF, // Set the color (use hex or RGB)
          backgroundColor: '#3c3c3c', // Optional: Set the background color
          points: 10, // Optional: Adjust the number of points
          maxDistance: 20, // Optional: Adjust the distance
          mouseControls: false, // Disable mouse interaction
          touchControls: false, // Disable touch interaction (if needed)
        })
      );
    }
    return () => {
      if (vantaEffect) vantaEffect.destroy();
    };
  }, [vantaEffect]);
  return (
    <>
      <div className={styles.home} ref={myRef}>
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
