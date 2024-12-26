import { useState, useEffect } from "react";
import styles from "./navigator.module.css";
import { Routes, Route, Link } from "react-router-dom";
import { BrowserProvider } from "ethers";

function Navigator() {
  const [walletConnected, setWalletConnected] = useState(false);
  const [userAddress, setUserAddress] = useState<string | null>(null);

  // ����ʱ���Ǯ������״̬
  useEffect(() => {
    const savedWalletConnected = localStorage.getItem("walletConnected");
    const savedUserAddress = localStorage.getItem("userAddress");

    if (savedWalletConnected === "true" && savedUserAddress) {
      setWalletConnected(true);
      setUserAddress(savedUserAddress);
    }
  }, []);

  // ����Ǯ������
  const connectWallet = async () => {
    if (typeof window.ethereum === "undefined") {
      alert("Please install MetaMask!");
      return;
    }

    try {
      const provider = new BrowserProvider(window.ethereum);

      // �����û�����Ǯ��
      const accounts = await provider.send("eth_requestAccounts", []);
      console.log("Connected accounts:", accounts);

      // ��ȡǩ���߲���ȡ��ַ
      const signer = await provider.getSigner();
      const address = await signer.getAddress();

      setUserAddress(address);
      setWalletConnected(true);

      // ����״̬�� localStorage
      localStorage.setItem("walletConnected", "true");
      localStorage.setItem("userAddress", address);

      console.log("Signer address:", address);
    } catch (error) {
      console.error("Failed to connect wallet:", error);
      alert("Failed to connect wallet!");
    }
  };
 // �Ͽ�Ǯ������
 const disconnectWallet = () => {
  setWalletConnected(false);
  setUserAddress(null);

  // ��� localStorage �е�״̬
  localStorage.removeItem("walletConnected");
  localStorage.removeItem("userAddress");

  console.log("Wallet disconnected.");
};
  return (
    <>
      <div className={styles.father}>
        <div className={styles.logo}>
          <Link to="/">
            <img
              src="../../../img/logo.jpg"
              alt="Logo"
              className={styles.logo_image}
            />
          </Link>
        </div>
        <div className={styles.DAO_name}>
          <Link to="/" className={styles.DAO_name_link}>
            Lumina DAO
          </Link>
        </div>
        <div className={styles.market}>
          <Link to="/market" className={styles.market_link}>
            Market
          </Link>
        </div>
        <div className={styles.deploy}>
          <Link to="/deploy" className={styles.deploy_link}>
            Deploy
          </Link>
        </div>
        <div className={styles.user}>
          <Link to="/user" className={styles.user_link}>
            User
          </Link>
        </div>
        <div className={styles.connect_wallet_button}>
          {!walletConnected ? (
            <div
              onClick={connectWallet}
              className={styles.connect_wallet_button}
            >
              Connect Wallet
            </div>
          ) : (
            <div className={styles.connected_state} onClick={disconnectWallet}>
              Connected
              <span className={styles.user_address}>
                ({userAddress?.slice(0, 6)}...{userAddress?.slice(-4)})
              </span>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default Navigator;
