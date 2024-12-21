// DepositPage.tsx
import React, { useState } from "react";
import Navigator from "../Navigator/Navigator";
import Footer from "../Footer/Footer";
import { Card, FormControl, InputLabel, MenuItem } from "@mui/material";
import styles from "./deposit.module.css";
// import Select, { SelectChangeEvent } from "@mui/material/Select";
import { Theme, useTheme } from "@mui/material/styles";
import OutlinedInput from "@mui/material/OutlinedInput";
import { Select } from '@mui/base/Select';
const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

const names = [
  "Oliver Hansen",
  "Van Henry",
  "April Tucker",
  "Ralph Hubbard",
  "Omar Alexander",
  "Carlos Abbott",
  "Miriam Wagner",
  "Bradley Wilkerson",
  "Virginia Andrews",
  "Kelly Snyder",
];

function getStyles(name: string, personName: string[], theme: Theme) {
  return {
    fontWeight: personName.includes(name)
      ? theme.typography.fontWeightMedium
      : theme.typography.fontWeightRegular,
  };
}
// ģ���������
const token = {
  symbol: "UNI",
  name: "Uniswap",
  balance: 1000, // �����û���1000��UNI����
};

const DepositPage = () => {
  const [amount, setAmount] = useState(0);
  const [stakingStatus, setStakingStatus] = useState("");

  // �����������Ѻ����
  const handleAmountChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setAmount(Number(event.target.value));
  };

  // ������Ѻ��ť���
  const handleStake = () => {
    if (amount <= 0) {
      setStakingStatus("��������ȷ����Ѻ����");
      return;
    }
    if (amount > token.balance) {
      setStakingStatus("����");
      return;
    }
    setStakingStatus("������Ѻ...");

    // ģ����Ѻ����������ɹ�
    setTimeout(() => {
      setStakingStatus("��Ѻ�ɹ���");
    }, 2000);
  };

  // ����ȡ����Ѻ��ť���
  const handleUnstake = () => {
    setStakingStatus("ȡ����Ѻ��...");

    // ģ��ȡ����Ѻ����������ɹ�
    setTimeout(() => {
      setStakingStatus("ȡ����Ѻ�ɹ���");
    }, 2000);
  };
  const theme = useTheme();
  const [personName, setPersonName] = React.useState<string[]>([]);

  const handleChange = (event: SelectChangeEvent<typeof personName>) => {
    const {
      target: { value },
    } = event;
    setPersonName(
      // On autofill we get a stringified value.
      typeof value === "string" ? value.split(",") : value
    );
  };
  return (
    <div className={styles.depositPage}>
      <Navigator />
      <div className={styles.content}>
        <div className={styles.cardContainer}>
          <div className={styles.card}>
            <h2 className={styles.title}>Stake</h2>
            <div className={styles.tokenInfo}>
              <div>
                <div>
                  <FormControl sx={{ m: 1, width: 300, backgroundColor:"rgb(96, 95, 95)", color: "white" }}>
                    <InputLabel id="demo-multiple-name-label">Name</InputLabel>
                    <Select
                      labelId="demo-multiple-name-label"
                      id="demo-multiple-name"
                      multiple
                      value={personName}
                      onChange={handleChange}
                      input={<OutlinedInput label="Name" />}
                      MenuProps={MenuProps}
                    >
                      {names.map((name) => (
                        <MenuItem
                          key={name}
                          value={name}
                          style={getStyles(name, personName, theme)}
                        >
                          {name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </div>
                {token.name} ({token.symbol})
              </div>
              <div>
                Balance: {token.balance} {token.symbol}
              </div>
            </div>
            <div className={styles.stakeSection}>
              <input
                type="number"
                className={styles.stakeInput}
                value={amount}
                onChange={handleAmountChange}
                placeholder="amount"
              />
              <div className={styles.stakeButtons}>
                <button onClick={handleStake} className={styles.stakeButton}>
                  Stake
                </button>
                <button
                  onClick={handleUnstake}
                  className={styles.unstakeButton}
                >
                  Cancel
                </button>
              </div>
              <div className={styles.status}>
                {stakingStatus && <span>{stakingStatus}</span>}
              </div>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default DepositPage;
