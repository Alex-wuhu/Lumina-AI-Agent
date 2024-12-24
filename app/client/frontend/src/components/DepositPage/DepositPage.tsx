import React, { useState, useEffect } from "react";
import Navigator from "../Navigator/Navigator";
import Footer from "../Footer/Footer";
import styles from "./deposit.module.css";
import { Select, Space, ConfigProvider, Input } from "antd";
import { DownOutlined } from "@ant-design/icons"; // 导入箭头图标
import { ethers } from "ethers"; // 导入 ethers.js V6

// 合约地址和 ABI
const contractAddress = "0x0aa156eebbe3a8921492491c3829444024502c9b"; // 替换为你的合约地址
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
// 初始化 provider（这里假设你使用 MetaMask）
const provider = new ethers.BrowserProvider(window.ethereum);
// 创建合约实例
const contract = new ethers.Contract(contractAddress, contractABI, await provider.getSigner());
// 模拟代币数据
const token = {
  symbol: "UNI",
  name: "Uniswap",
  balance: 1000, // 假设用户有1000个UNI代币
};

const DepositPage = () => {
  const [amount, setAmount] = useState(0);
  const [stakingStatus, setStakingStatus] = useState("");
  const [inputValue, setInputValue] = useState("0"); // 使用字符串来处理空值和零的显示
  const [selectedToken, setSelectedToken] = useState("BNB");

  // 处理输入的质押数量
  const handleAmountChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value);
  };

  // 处理代币选择变化
  const handleChange = (value: string) => {
    setSelectedToken(value);
    console.log(`selected ${value}`);
  };

  // 初始化 ethers.js 提供的 Web3 连接
  const getWeb3Provider = () => {
    const provider = new ethers.BrowserProvider(window.ethereum);
    return provider;
  };

  // 获取合约实例
  const getContract = async (provider: ethers.BrowserProvider) => {
    const signer = await provider.getSigner(); // 使用 await 获取 Signer 实例
    const contract = new ethers.Contract(contractAddress, contractABI, signer);
    return contract;
  };

  // 处理质押按钮点击
  const handleStake = async () => {
    const numericAmount = Number(inputValue);
    if (numericAmount <= 0) {
      setStakingStatus("请输入正确的质押数量");
      return;
    }
    if (numericAmount > token.balance) {
      setStakingStatus("余额不足");
      return;
    }
    setStakingStatus("正在质押...");
  
    try {
      // 获取 signer 对象
      const signer = await provider.getSigner();
  
      if (selectedToken === "BNB") {
        // 使用 depositETH 进行质押
        console.log(ethers.parseEther(inputValue));
        
        try {
          const tx = await contract.depositETH(
            ethers.parseEther(inputValue), // 转换为 wei
          );
          
          await tx.wait();
        } catch (error) {
          console.error("交易失败，错误信息：", error);
          setStakingStatus("质押失败！");
        }
        
        setStakingStatus("质押成功！");
      } else {
        // 使用 depositERC20 进行质押
        const tokenAddress = "<ERC20_TOKEN_ADDRESS>"; // 替换为你要质押的 ERC-20 代币地址
  
        // 创建 ERC-20 代币合约实例
        const tokenContract = new ethers.Contract(tokenAddress, [
          "function approve(address spender, uint256 amount) public returns (bool)",
        ], signer);
  
        // 创建质押合约实例
        const agentContract = new ethers.Contract(contractAddress, [
          "function depositERC20(address tokenAddress, uint256 amount) external", // 假设你有该函数
        ], signer);
  
        // 授权合约转账代币
        const amountInWei = ethers.parseEther(inputValue); // 代币质押数量
        const approvalTx = await tokenContract.approve(contractAddress, amountInWei);
        await approvalTx.wait();
  
        // 调用 depositERC20 方法进行质押
        const depositTx = await agentContract.depositERC20(tokenAddress, amountInWei);
        await depositTx.wait();
  
        setStakingStatus("质押成功！");
      }
    } catch (error) {
      console.error("质押失败", error);
      setStakingStatus("质押失败！");
    }
  };
  
  

  // 处理取消质押按钮点击
  const handleUnstake = async () => {
    setStakingStatus("取消质押中...");

    // 模拟取消质押操作，假设成功
    setTimeout(() => {
      setStakingStatus("取消质押成功！");
    }, 2000);
  };

  // 点击其他区域时，如果 input 为空，则恢复为0
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
                      suffixIcon={<DownOutlined style={{ color: "white" }} />} // 自定义下拉箭头
                    />
                  </Space>
                </div>
              </div>
              {/* 将 Button 替换为 div，并为其添加点击事件 */}
              <div 
                className={styles.stake_button} 
                onClick={handleStake} // 处理点击事件
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
