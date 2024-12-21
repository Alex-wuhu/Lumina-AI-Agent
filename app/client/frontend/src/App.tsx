// App.tsx
import React from "react";
import { BrowserRouter as Router } from "react-router-dom"; // 在根组件中使用 Router
import RoutesConfig from "./routes"; // 导入路由配置

import "./App.css";

function App() {
  return (
    <>
      <RoutesConfig /> {/* 使用路由配置 */}
    </>
  );
}

export default App;
