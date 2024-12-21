import { useState } from "react";
import styles from "./navigator.module.css";
import { Routes, Route, Link } from "react-router-dom";
import { BrowserProvider } from "ethers";

function Navigator() {
  const [walletConnected, setWalletConnected] = useState(false);
  const [userAddress, setUserAddress] = useState<string | null>(null);

  // 连接钱包函数
  const connectWallet = async () => {
    if (typeof window.ethereum === "undefined") {
      alert("Please install MetaMask!");
      return;
    }

    try {
      // 创建 BrowserProvider 实例
      const provider = new BrowserProvider(window.ethereum);

      // 请求用户连接钱包
      const accounts = await provider.send("eth_requestAccounts", []);
      console.log("Connected accounts:", accounts);

      // 获取签名者并提取地址
      const signer = await provider.getSigner();
      const address = await signer.getAddress();

      setUserAddress(address);
      setWalletConnected(true);
      console.log("Signer address:", address);
    } catch (error) {
      console.error("Failed to connect wallet:", error);
      alert("Failed to connect wallet!");
    }
  };

  return (
    <>
      <div className={styles.father}>
        <div className={styles.logo}>
          <Link to="/">
            <img src="../../../img/logo.jpg" alt="Logo" className={styles.logo_image} />
          </Link>
        </div>
        <div className={styles.DAO_name}>
          <Link to="/" className={styles.DAO_name_link}>
            Lumina DAO
          </Link>
        </div>
        <div className={styles.home}>
          <Link to="/" className={styles.home_link}>Home</Link>
        </div>
        <div className={styles.user}>
          <Link to="/user" className={styles.user_link}>User</Link>
        </div>
        <div className={styles.connect_wallet_button}>
          {!walletConnected ? (
            <div onClick={connectWallet}>Connect Wallet</div>
          ) : (
            <span>Connected: {userAddress?.slice(0, 6)}...{userAddress?.slice(-4)}</span>
          )}
        </div>
      </div>
    </>
  );
}

export default Navigator;
