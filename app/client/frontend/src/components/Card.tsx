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
import { red } from "@mui/material/colors";
import SendIcon from "@mui/icons-material/Send";
import DiamondIcon from "@mui/icons-material/Diamond";
import MoreVertIcon from "@mui/icons-material/MoreVert";
import { Button } from "@mui/material";
import { ethers } from "ethers";
import { Routes, Route, Link } from "react-router-dom";


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

export default function RecipeReviewCard() {
  const [contractBalance, setContractBalance] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);

  // 合约地址和ABI
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
  ];

  // 获取合约余额
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

  // 调用 depositETH
  const depositETH = async () => {
    try {
      if (!window.ethereum) {
        alert("Please install MetaMask!");
        return;
      }

      setIsLoading(true);

      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();
      const contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, signer);

      // 调用 depositETH 方法，传入 0.1 TBNB
      const tx = await contract.depositETH({
        value: ethers.parseEther("0.1"), // 存入 0.1 TBNB
      });

      await tx.wait(); // 等待交易确认

      alert("Deposited 0.1 TBNB successfully!");
      await fetchContractBalance(); // 更新合约余额
    } catch (error) {
      console.error("Error depositing TBNB:", error);
      alert("Failed to deposit TBNB. Make sure you are the contract owner.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card sx={{ maxWidth: 345, backgroundColor: "lightblue" }}>
      <CardHeader
        avatar={
          <Avatar sx={{ bgcolor: red[700] }} aria-label="recipe">
            U
          </Avatar>
        }
        action={
          <IconButton aria-label="settings">
            <MoreVertIcon />
          </IconButton>
        }
        title="AGENT"
        subheader="December 14, 2024"
      />
      <CardMedia
        component="img"
        height="194"
        image="../../public/img/metaverse.jpg"
        alt="Paella dish"
      />
      <CardContent>
        <Typography variant="body2" sx={{ color: "text.secondary" }}>
          This AI agent was developed by Lumina DAO.
        </Typography>
        {contractBalance !== null && (
          <Typography variant="body2" sx={{ color: "text.secondary", marginTop: "1rem" }}>
            Contract Balance: {contractBalance} TBNB
          </Typography>
        )}
      </CardContent>
      <CardActions disableSpacing sx={{ justifyContent: "flex-end" }}>
        <Link to="/deposit">
        <Button
          variant="contained"
          endIcon={<SendIcon />}
          sx={{ backgroundColor: "orange" }}
          disabled={isLoading}
        >
          {isLoading ? "Depositing..." : "Deposit"}
        </Button>
        </Link>

        <Button
          variant="contained"
          endIcon={<DiamondIcon />}
          sx={{ marginLeft: "1vw", backgroundColor: "grey" }}
          onClick={fetchContractBalance}
        >
          Buy NFT
        </Button>
      </CardActions>
    </Card>
  );
}
