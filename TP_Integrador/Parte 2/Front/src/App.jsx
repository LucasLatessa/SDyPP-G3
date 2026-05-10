import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import TransactionPage from './pages/TransactionPage';
import BlockchainPage from './pages/BlockchainPage';
import './index.css';

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<TransactionPage />} />
        <Route path="/blockchain" element={<BlockchainPage />} />
      </Routes>
    </BrowserRouter>
  );
}
