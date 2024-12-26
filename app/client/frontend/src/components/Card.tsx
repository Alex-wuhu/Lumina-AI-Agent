import * as React from "react";
import { styled } from "@mui/material/styles";
import Card from "@mui/material/Card";
import CardHeader from "@mui/material/CardHeader";
import CardMedia from "@mui/material/CardMedia";
import CardContent from "@mui/material/CardContent";
import CardActions from "@mui/material/CardActions";
import Avatar from "@mui/material/Avatar";
import IconButton, { IconButtonProps } from "@mui/material/IconButton";
import Typography from "@mui/material/Typography";
import { brown, red } from "@mui/material/colors";
import SendIcon from "@mui/icons-material/Send";
import DiamondIcon from "@mui/icons-material/Diamond";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import { Button } from "@mui/material";
import { ethers } from "ethers";
import { Link } from "react-router-dom";
interface RecipeReviewCardProps {
  image: string;  // ����ͼƬ URL ��Ϊ prop
}

interface ExpandMoreProps extends IconButtonProps {
  expand: boolean;
}

const ExpandMore = styled((props: ExpandMoreProps) => {
  const { expand, ...other } = props;
  return <IconButton {...other} />;
})(({ theme }) => ({
  marginLeft: "auto",
  transition: theme.transitions.create("transform", {
    duration: theme.transitions.duration.shortest,
  }),
}));

export default function RecipeReviewCard({ image }: RecipeReviewCardProps) {
  const [contractBalance, setContractBalance] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);
  const [newOwner, setNewOwner] = React.useState<string>("");
  const CONTRACT_ADDRESS = "0xbb927cbdedfe4a08f7d1fcb8a1df016536ff6de7";
  const CONTRACT_ABI = [
    {
      inputs: [],
      name: "depositETH",
      outputs: [],
      stateMutability: "payable",
      type: "function",
    },
    {
      inputs: [],
      name: "contractETHBalance",
      outputs: [{ internalType: "uint256", name: "", type: "uint256" }],
      stateMutability: "view",
      type: "function",
    },
    {
      inputs: [{ internalType: "address", name: "newOwner", type: "address" }],
      name: "transferOwnership",
      outputs: [],
      stateMutability: "nonpayable",
      type: "function",
    },
  ];

// ��ȡ��ǰ��¼��Ǯ����ַ
React.useEffect(() => {
  const fetchWalletAddress = async () => {
    if (!window.ethereum) {
      alert("Please install MetaMask!");
      return;
    }

    try {
      const provider = new ethers.BrowserProvider(window.ethereum);
      const accounts = await provider.listAccounts();
      if (accounts.length > 0) {
        setNewOwner(accounts[0]); // Ĭ������Ϊ��ǰ��¼�˻���ַ
      }
    } catch (error) {
      console.error("Failed to fetch wallet address:", error);
    }
  };

  fetchWalletAddress();

  // �����˻��л�
  window.ethereum?.on("accountsChanged", (accounts: string[]) => {
    if (accounts.length > 0) {
      setNewOwner(accounts[0]);
    }
  });
  fetchContractBalance();
  return () => {
    window.ethereum?.removeListener("accountsChanged", (accounts: string[]) => {
      if (accounts.length > 0) {
        setNewOwner(accounts[0]);
      }
    });
  };
}, []);

  // ��ȡ��Լ���
  const fetchContractBalance = async () => {
    try {
      if (!window.ethereum) {
        alert("Please install MetaMask!");
        return;
      }

      const provider = new ethers.BrowserProvider(window.ethereum);
      const contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, provider);

      const balance = await contract.contractETHBalance();
      setContractBalance(ethers.formatEther(balance));
    } catch (error) {
      console.error("Error fetching contract balance:", error);
      alert("Failed to fetch contract balance.");
    }
  };
// ת�ƺ�Լ����Ȩ
const transferOwnership = async () => {
  if (!newOwner) {
    alert("No wallet address detected. Please connect your wallet.");
    return;
  }

  try {
    if (!window.ethereum) {
      alert("Please install MetaMask!");
      return;
    }

    setIsLoading(true);

    const provider = new ethers.BrowserProvider(window.ethereum);
    const signer = await provider.getSigner();
    const contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, signer);

    const tx = await contract.transferOwnership(newOwner);
    await tx.wait(); // �ȴ�����ȷ��

    alert(`Ownership transferred to ${newOwner}!`);
  } catch (error) {
    console.error("Error transferring ownership:", error);
    alert("Failed to transfer ownership.");
  } finally {
    setIsLoading(false);
  }
};


  return (
    <Card sx={{ maxWidth: 345, backgroundColor: "rgb(99, 90, 90)", color:"whitesmoke" }}>
      <CardHeader
        avatar={<Avatar sx={{ bgcolor: brown[800] }} aria-label="recipe">U</Avatar>}
        action={<IconButton aria-label="settings"><MoreVertIcon /></IconButton>}
        title="AGENT"
        subheader="December 14, 2024"
        sx={{ 
          "& .MuiCardHeader-subheader": {
            color: "whitesmoke", // �޸�Ϊ����Ҫ����ɫ��������ɫ
          }
        }}
      />
      <CardMedia component="img" height="194" image={image} alt="Paella dish" /> {/* ʹ�ô��ݵ�ͼƬ URL */}
      <CardContent>
        <Typography variant="body2" sx={{ color: "whitesmoke" }}>
          This AI agent has {contractBalance} BNB in total.
        </Typography>
        
      </CardContent>
      <CardActions disableSpacing sx={{ justifyContent: "flex-end" }}>
      <Link to="/deposit">
        <Button
          variant="contained"
          endIcon={<SendIcon />}
          sx={{ backgroundColor: "orange" }}
          disabled={isLoading}
        >
        Deposit
        </Button>
        </Link>
        <Button
          variant="contained"
          endIcon={<SendIcon />}
          sx={{ backgroundColor: "grey", marginLeft:"1vw" }}
          disabled={isLoading}
          onClick={transferOwnership} // ���� transferOwnership ����
        >
          Buy NFT
        </Button>
      </CardActions>
    </Card>
  );
}
