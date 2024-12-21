import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom'; // 导入 BrowserRouter
import './index.css';

import App from './App.tsx';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter> {/* 使用 BrowserRouter 包裹 App 组件 */}
      <App />
    </BrowserRouter>
  </StrictMode>,
);
