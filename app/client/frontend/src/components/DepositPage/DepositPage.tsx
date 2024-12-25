import Navigator from "../Navigator/Navigator";
import Footer from "../Footer/Footer";
import { Select, Space, ConfigProvider, Input } from "antd";
import { DownOutlined } from "@ant-design/icons"; // 导入箭头图标
import { ethers } from "ethers"; // 导入 ethers.js V6
import React, { useState, useEffect, useRef } from "react";
import NET from "vanta/dist/vanta.net.min";
import styles from "./deposit.module.css";


// 合约地址和 ABI
const contractAddress = "0x0aa156eebbe3a8921492491c3829444024502c9b"; // 替换为你的合约地址
const contractABI = [
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_owner",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "_authorizedBackend",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "_pancakeRouter",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "_WBNB",
				"type": "address"
			}
		],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "previousBackend",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "newBackend",
				"type": "address"
			}
		],
		"name": "AuthorizedBackendChanged",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "user",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "newBalance",
				"type": "uint256"
			}
		],
		"name": "ETHBalanceUpdated",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "previousOwner",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "OwnershipTransferred",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "user",
				"type": "address"
			},
			{
				"indexed": true,
				"internalType": "address",
				"name": "token",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "newBalance",
				"type": "uint256"
			}
		],
		"name": "TokenBalanceUpdated",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"internalType": "address",
				"name": "user",
				"type": "address"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "amountIn",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "address[]",
				"name": "path",
				"type": "address[]"
			},
			{
				"indexed": false,
				"internalType": "uint256[]",
				"name": "amounts",
				"type": "uint256[]"
			}
		],
		"name": "TradeExecuted",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "WBNB",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "authorizedBackend",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "contractETHBalance",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
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
	{
		"inputs": [],
		"name": "depositETH",
		"outputs": [],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getETHBalance",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "tokenAddress",
				"type": "address"
			}
		],
		"name": "getTokenBalance",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "pancakeRouter",
		"outputs": [
			{
				"internalType": "contract IPancakeRouter",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "newBackend",
				"type": "address"
			}
		],
		"name": "setAuthorizedBackend",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "user",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "amountOutMin",
				"type": "uint256"
			},
			{
				"internalType": "address[]",
				"name": "path",
				"type": "address[]"
			},
			{
				"internalType": "uint256",
				"name": "deadline",
				"type": "uint256"
			}
		],
		"name": "swapETHForTokens",
		"outputs": [],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "user",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "amountIn",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "amountOutMin",
				"type": "uint256"
			},
			{
				"internalType": "address[]",
				"name": "path",
				"type": "address[]"
			},
			{
				"internalType": "uint256",
				"name": "deadline",
				"type": "uint256"
			}
		],
		"name": "swapTokensForETH",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "user",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "amountIn",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "amountOutMin",
				"type": "uint256"
			},
			{
				"internalType": "address[]",
				"name": "path",
				"type": "address[]"
			},
			{
				"internalType": "uint256",
				"name": "deadline",
				"type": "uint256"
			}
		],
		"name": "swapTokensForTokens",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "transferOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "userETHBalances",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			},
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "userTokenBalances",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
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
		"name": "withdrawERC20",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_amount",
				"type": "uint256"
			}
		],
		"name": "withdrawETH",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"stateMutability": "payable",
		"type": "receive"
	}
];

// 初始化 provider（这里假设你使用 MetaMask）
const provider = new ethers.BrowserProvider(window.ethereum);
// 创建合约实例
const contract = new ethers.Contract(
  contractAddress,
  contractABI,
  await provider.getSigner()
);
// 模拟代币数据
const tokenAddresses = {
  ETH: "<USDT_ADDRESS>",
  BUSD: "<BUSD_ADDRESS>",
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

  // 输入值验证
  if (isNaN(numericAmount) || numericAmount <= 0) {
    setStakingStatus("请输入正确的质押数量");
    return;
  }

  setStakingStatus("正在质押...");

  try {
    // 获取 signer 对象
    const signer = await provider.getSigner();

    if (selectedToken === "BNB") {
      await stakeBNB(inputValue, signer);
    } else {
      const tokenAddress = "<ERC20_TOKEN_ADDRESS>"; // 替换为目标 ERC-20 代币地址
      await stakeERC20(inputValue, tokenAddress, signer);
    }

    setStakingStatus("质押成功！");
  } catch (error) {
    console.error("质押失败：", error);
    setStakingStatus("质押失败！请检查输入并重试。");
  }
};

// 处理 BNB 质押
const stakeBNB = async (amount: any, signer: any) => {
  try {
    const tx = await contract.depositETH({
      value:BigInt("1000") // 转换为 wei

    });
    await tx.wait();
  } catch (error) {
    throw new Error(`BNB 质押失败: ${error.message}`);
  }
};

// 处理 ERC-20 代币质押
const stakeERC20 = async (amount: any, tokenAddress: any, signer: any) => {
  try {
    const tokenContract = new ethers.Contract(
      tokenAddress,
      [
        "function approve(address spender, uint256 amount) public returns (bool)",
      ],
      signer
    );

    const amountInWei = ethers.parseUnits(amount); // 转换为 wei
    const contractAddress = "<STAKING_CONTRACT_ADDRESS>"; // 替换为质押合约地址

    // 授权代币转账
    const approvalTx = await tokenContract.approve(contractAddress, amountInWei);
    await approvalTx.wait();

    // 调用质押方法
    const depositTx = await contract.depositERC20(
      tokenAddress,
      amountInWei
    );
    await depositTx.wait();
  } catch (error) {
    throw new Error(`ERC-20 质押失败: ${error.message}`);
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
    <ConfigProvider
      theme={{
        components: {
          Select: {
            activeBorderColor: "rgba(173, 173, 173, 0.5)",
            hoverBorderColor: "rgba(173, 173, 173, 0.5)",
            selectorBg: "rgba(34, 34, 34,0.5)",
            colorTextPlaceholder: "white",
            multipleItemBg: "rgba(34, 34, 34,0.5)",
            optionActiveBg: "rgb(60,60,60)",
            optionSelectedBg: "rgb(60,60,60)",
            colorText: "white",
            colorBgElevated: "rgba(34, 34, 34,0.5)",
            colorBorder: "rgba(173, 173, 173, 0.5)",
          },
          Input: {
            colorBorder: "rgba(34, 34, 34,0)",
            hoverBorderColor: "rgba(34, 34, 34,0)",
            activeBorderColor: "rgba(34, 34, 34,0)",
            colorBgContainer: "rgba(34, 34, 34,0)",
            inputFontSize: 40,
          },
        },
      }}
    >
      <div className={styles.depositPage} ref={myRef}>
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
                        { value: "BUSD", label: "BUSD" },
                      ]}
                      suffixIcon={<DownOutlined style={{ color: "white" }} />} // 自定义下拉箭头
                    />
                  </Space>
                </div>
              </div>
              <div
                className={styles.stake_button}
                onClick={handleStake} 
              >
                <div className={styles.customButton}>Stake</div>
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
