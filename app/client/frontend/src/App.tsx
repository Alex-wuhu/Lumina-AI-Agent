// App.tsx
import React from "react";
import { BrowserRouter as Router } from "react-router-dom"; // �ڸ������ʹ�� Router
import RoutesConfig from "./routes"; // ����·������

import "./App.css";

function App() {
  return (
    <>
      <RoutesConfig /> {/* ʹ��·������ */}
    </>
  );
}

export default App;
