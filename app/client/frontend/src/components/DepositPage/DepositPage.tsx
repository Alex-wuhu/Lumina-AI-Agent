import Navigator from "../Navigator/Navigator";
import Footer from "../Footer/Footer";
import { Select, Space, ConfigProvider, Input } from "antd";
import { DownOutlined } from "@ant-design/icons"; // �����ͷͼ��
import { ethers } from "ethers"; // ���� ethers.js V6
import React, { useState, useEffect, useRef } from "react";
import NET from "vanta/dist/vanta.net.min";
import styles from "./deposit.module.css";


// ��Լ��ַ�� ABI
const contractAddress = "0x0aa156eebbe3a8921492491c3829444024502c9b"; // �滻Ϊ��ĺ�Լ��ַ
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

// ��ʼ�� provider�����������ʹ�� MetaMask��
const provider = new ethers.BrowserProvider(window.ethereum);
// ������Լʵ��
const contract = new ethers.Contract(
  contractAddress,
  contractABI,
  await provider.getSigner()
);
// ģ���������
const tokenAddresses = {
  ETH: "<USDT_ADDRESS>",
  BUSD: "<BUSD_ADDRESS>",
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

  // ����ֵ��֤
  if (isNaN(numericAmount) || numericAmount <= 0) {
    setStakingStatus("��������ȷ����Ѻ����");
    return;
  }

  setStakingStatus("������Ѻ...");

  try {
    // ��ȡ signer ����
    const signer = await provider.getSigner();

    if (selectedToken === "BNB") {
      await stakeBNB(inputValue, signer);
    } else {
      const tokenAddress = "<ERC20_TOKEN_ADDRESS>"; // �滻ΪĿ�� ERC-20 ���ҵ�ַ
      await stakeERC20(inputValue, tokenAddress, signer);
    }

    setStakingStatus("��Ѻ�ɹ���");
  } catch (error) {
    console.error("��Ѻʧ�ܣ�", error);
    setStakingStatus("��Ѻʧ�ܣ��������벢���ԡ�");
  }
};

// ���� BNB ��Ѻ
const stakeBNB = async (amount: any, signer: any) => {
  try {
    const tx = await contract.depositETH({
      value:BigInt("1000") // ת��Ϊ wei

    });
    await tx.wait();
  } catch (error) {
    throw new Error(`BNB ��Ѻʧ��: ${error.message}`);
  }
};

// ���� ERC-20 ������Ѻ
const stakeERC20 = async (amount: any, tokenAddress: any, signer: any) => {
  try {
    const tokenContract = new ethers.Contract(
      tokenAddress,
      [
        "function approve(address spender, uint256 amount) public returns (bool)",
      ],
      signer
    );

    const amountInWei = ethers.parseUnits(amount); // ת��Ϊ wei
    const contractAddress = "<STAKING_CONTRACT_ADDRESS>"; // �滻Ϊ��Ѻ��Լ��ַ

    // ��Ȩ����ת��
    const approvalTx = await tokenContract.approve(contractAddress, amountInWei);
    await approvalTx.wait();

    // ������Ѻ����
    const depositTx = await contract.depositERC20(
      tokenAddress,
      amountInWei
    );
    await depositTx.wait();
  } catch (error) {
    throw new Error(`ERC-20 ��Ѻʧ��: ${error.message}`);
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
                      suffixIcon={<DownOutlined style={{ color: "white" }} />} // �Զ���������ͷ
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
