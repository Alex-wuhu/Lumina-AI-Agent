// routes/index.tsx
import React from "react";
import { Routes, Route } from "react-router-dom";
import Home from "../components/Home"; // 主页面
import DepositPage from "../components/DepositPage/DepositPage"; // 存款页面
import Market from "../components/Market/Market"
const RoutesConfig = () => {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/deposit" element={<DepositPage />} />
      <Route path="/market" element={<Market />} />
    </Routes>
  );
};

export default RoutesConfig;
