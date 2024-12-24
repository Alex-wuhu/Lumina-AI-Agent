import React, { useState, useEffect } from "react";
import Navigator from "../Navigator/Navigator";
import Footer from "../Footer/Footer";
import styles from "./deposit.module.css";
import { Select, Space, ConfigProvider, Input } from "antd";
import { DownOutlined } from "@ant-design/icons"; // �����ͷͼ��
import { ethers } from "ethers"; // ���� ethers.js V6

// ��Լ��ַ�� ABI
const contractAddress = "0x0aa156eebbe3a8921492491c3829444024502c9b"; // �滻Ϊ��ĺ�Լ��ַ
const contractABI = [
  // depositETH
  {
    "inputs": [
      {
        "internalType": "uint256",
        "name": "_amount",
        "type": "uint256"
      }
    ],
    "name": "depositETH",
    "outputs": [],
    "stateMutability": "payable",
    "type": "function"
  },
  // depositERC20
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "tokenAddress",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "depositERC20",
    "outputs": [],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  // Approve function for ERC20 tokens
  {
    "inputs": [
      {
        "internalType": "address",
        "name": "spender",
        "type": "address"
      },
      {
        "internalType": "uint256",
        "name": "amount",
        "type": "uint256"
      }
    ],
    "name": "approve",
    "outputs": [
      {
        "internalType": "bool",
        "name": "",
        "type": "bool"
      }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  }
];
// ��ʼ�� provider�����������ʹ�� MetaMask��
const provider = new ethers.BrowserProvider(window.ethereum);
// ������Լʵ��
const contract = new ethers.Contract(contractAddress, contractABI, await provider.getSigner());
// ģ���������
const token = {
  symbol: "UNI",
  name: "Uniswap",
  balance: 1000, // �����û���1000��UNI����
};

const DepositPage = () => {
  const [amount, setAmount] = useState(0);
  const [stakingStatus, setStakingStatus] = useState("");
  const [inputValue, setInputValue] = useState("0"); // ʹ���ַ����������ֵ�������ʾ
  const [selectedToken, setSelectedToken] = useState("BNB");

  // �����������Ѻ����
  const handleAmountChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value);
  };

  // �������ѡ��仯
  const handleChange = (value: string) => {
    setSelectedToken(value);
    console.log(`selected ${value}`);
  };

  // ��ʼ�� ethers.js �ṩ�� Web3 ����
  const getWeb3Provider = () => {
    const provider = new ethers.BrowserProvider(window.ethereum);
    return provider;
  };

  // ��ȡ��Լʵ��
  const getContract = async (provider: ethers.BrowserProvider) => {
    const signer = await provider.getSigner(); // ʹ�� await ��ȡ Signer ʵ��
    const contract = new ethers.Contract(contractAddress, contractABI, signer);
    return contract;
  };

  // ������Ѻ��ť���
  const handleStake = async () => {
    const numericAmount = Number(inputValue);
    if (numericAmount <= 0) {
      setStakingStatus("��������ȷ����Ѻ����");
      return;
    }
    if (numericAmount > token.balance) {
      setStakingStatus("����");
      return;
    }
    setStakingStatus("������Ѻ...");
  
    try {
      // ��ȡ signer ����
      const signer = await provider.getSigner();
  
      if (selectedToken === "BNB") {
        // ʹ�� depositETH ������Ѻ
        console.log(ethers.parseEther(inputValue));
        
        try {
          const tx = await contract.depositETH(
            ethers.parseEther(inputValue), // ת��Ϊ wei
          );
          
          await tx.wait();
        } catch (error) {
          console.error("����ʧ�ܣ�������Ϣ��", error);
          setStakingStatus("��Ѻʧ�ܣ�");
        }
        
        setStakingStatus("��Ѻ�ɹ���");
      } else {
        // ʹ�� depositERC20 ������Ѻ
        const tokenAddress = "<ERC20_TOKEN_ADDRESS>"; // �滻Ϊ��Ҫ��Ѻ�� ERC-20 ���ҵ�ַ
  
        // ���� ERC-20 ���Һ�Լʵ��
        const tokenContract = new ethers.Contract(tokenAddress, [
          "function approve(address spender, uint256 amount) public returns (bool)",
        ], signer);
  
        // ������Ѻ��Լʵ��
        const agentContract = new ethers.Contract(contractAddress, [
          "function depositERC20(address tokenAddress, uint256 amount) external", // �������иú���
        ], signer);
  
        // ��Ȩ��Լת�˴���
        const amountInWei = ethers.parseEther(inputValue); // ������Ѻ����
        const approvalTx = await tokenContract.approve(contractAddress, amountInWei);
        await approvalTx.wait();
  
        // ���� depositERC20 ����������Ѻ
        const depositTx = await agentContract.depositERC20(tokenAddress, amountInWei);
        await depositTx.wait();
  
        setStakingStatus("��Ѻ�ɹ���");
      }
    } catch (error) {
      console.error("��Ѻʧ��", error);
      setStakingStatus("��Ѻʧ�ܣ�");
    }
  };
  
  

  // ����ȡ����Ѻ��ť���
  const handleUnstake = async () => {
    setStakingStatus("ȡ����Ѻ��...");

    // ģ��ȡ����Ѻ����������ɹ�
    setTimeout(() => {
      setStakingStatus("ȡ����Ѻ�ɹ���");
    }, 2000);
  };

  // �����������ʱ����� input Ϊ�գ���ָ�Ϊ0
  useEffect(() => {
    const handleClickOutside = () => {
      if (inputValue === "") {
        setInputValue("0");
      }
    };

    document.addEventListener("click", handleClickOutside);
    return () => {
      document.removeEventListener("click", handleClickOutside);
    };
  }, [inputValue]);

  return (
    <ConfigProvider
      theme={{
        components: {
          Select: {
            activeBorderColor: "rgba(173, 173, 173, 0.5)",
            hoverBorderColor: "rgba(173, 173, 173, 0.5)",
            selectorBg: "rgb(34, 34, 34)",
            colorTextPlaceholder: "white",
            multipleItemBg: "rgb(34, 34, 34)",
            optionActiveBg: "rgb(60,60,60)",
            optionSelectedBg: "rgb(60,60,60)",
            colorText: "white",
            colorBgElevated: "rgb(34, 34, 34)",
            colorBorder: "rgba(173, 173, 173, 0.5)",
          },
          Input: {
            colorBorder: "rgb(34, 34, 34)",
            hoverBorderColor: "rgb(34, 34, 34)",
            activeBorderColor: "rgb(34, 34, 34)",
            colorBgContainer: "rgb(34, 34, 34)",
            inputFontSize: 40,
          },
        },
      }}
    >
      <div className={styles.depositPage}>
        <Navigator />
        <div className={styles.content}>
          <div className={styles.cardContainer}>
            <div className={styles.card}>
              <div>
                <h2 className={styles.title}>Stake</h2>
              </div>
              <div className={styles.stake_content}>
                <div>
                  <Input
                    min={0}
                    style={{
                      width: "20vw",
                      height: "10vh",
                      color: "rgba(173, 173, 173, 0.7)",
                    }}
                    value={inputValue}
                    onChange={handleAmountChange}
                  />
                </div>
                <div className={styles.tokenInfo}>
                  <Space wrap>
                    <Select
                      defaultValue="BNB"
                      style={{ width: "10vw", height: "8vh", color: "white" }}
                      onChange={handleChange}
                      options={[
                        { value: "BNB", label: "BNB" },
                        { value: "ETH", label: "ETH" },
                        { value: "USDT", label: "USDT" },
                      ]}
                      suffixIcon={<DownOutlined style={{ color: "white" }} />} // �Զ���������ͷ
                    />
                  </Space>
                </div>
              </div>
              {/* �� Button �滻Ϊ div����Ϊ����ӵ���¼� */}
              <div 
                className={styles.stake_button} 
                onClick={handleStake} // �������¼�
              >
                <div className={styles.customButton}>
                  Stake
                </div>
              </div>
            </div>
          </div>
        </div>
        <Footer />
      </div>
    </ConfigProvider>
  );
};

export default DepositPage;
