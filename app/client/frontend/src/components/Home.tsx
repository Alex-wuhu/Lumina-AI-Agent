import Navigator from './Navigator/Navigator'
import Footer from './Footer/Footer'
import Card from './Card'
import styles from "./home.module.css"
function Home() {
  return (
    <>
      <div className={styles.home}>
        <Navigator></Navigator>
        <div className={styles.content}>
          <div className={styles.card}>
          <Card ></Card>
          </div>
          <div className={styles.card}>
          <Card ></Card>
          </div>
          <div className={styles.card}>
          <Card ></Card>
          </div>
          <div className={styles.card}>
          <Card ></Card>
          </div>
          <div className={styles.card}>
          <Card ></Card>
          </div>
          <div className={styles.card}>
          <Card ></Card>
          </div>
          <div className={styles.card}>
          <Card ></Card>
          </div>
        </div>
      </div>
    </>
  )
}

export default Home
