import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { MainPage } from './pages/MainPage';
import './Main.css';

export function App() {
  return (
    <div className="min-h-screen bg-bg text-text">
      <Routes>
        <Route path="/" element={<MainPage />} />
      </Routes>
    </div>
  );
}
