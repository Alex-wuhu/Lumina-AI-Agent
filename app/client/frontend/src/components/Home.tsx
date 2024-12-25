import Navigator from "./Navigator/Navigator";
import Footer from "./Footer/Footer";
import React, { useState, useEffect, useRef } from "react";
import NET from "vanta/dist/vanta.net.min";
import { Link } from "react-router-dom";

import styles from "./home.module.css";

function Home() {
  const [vantaEffect, setVantaEffect] = useState(null);
  const myRef = useRef(null);
  useEffect(() => {
    if (!vantaEffect) {
      setVantaEffect(
        NET({
          el: myRef.current,
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
          <div className={styles.welcome}>WELCOME TO LUMINA DAO</div>
          <div className={styles.feature}>
            <Link to="https://github.com/Alex-wuhu/Lumina-AI-Agent" className={styles.doc_link}>
              <div className={styles.doc}>Doc</div>
            </Link>
            <Link to="/market" className={styles.market_link}>
              <div className={styles.market}>Market</div>
            </Link>

            <Link to="/deploy" className={styles.deploy_link}>
              <div className={styles.deploy}>Deploy</div>
            </Link>
          </div>
          <div className={styles.intro}>
            <div className={styles.intro_img}>
            <img src="../public/img/metaverse2.png" alt="Description of the image" style={{ width: '100%', height: 'auto' }} />
            </div>
            <div className={styles.intro_content}>
              <div className={styles.intro_content_title}>
                The most innovative web3 AI agent platform
              </div>
              <div className={styles.intro_content_text}>
                Lumina can help users train their decentralized AI agent in the crypto market and sold them to make profit.
              </div>
              <div className={styles.intro_content_buttons}>
                <Link to="https://github.com/Alex-wuhu/Lumina-AI-Agent" className={styles.getstart_link}>
                <div className={styles.getstart}>
                  Get Start
                </div>
                </Link>
              </div>
            </div>
          </div>
        </div>
        <Footer />
      </div>
    </>
  );
}

export default Home;
