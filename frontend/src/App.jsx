import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import LiveBetting from './components/LiveBetting';
import './styles/main.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-brand">
          <span className="brand-icon">⚔️</span>
          <h1>LoL Bet Analyzer</h1>
          <span className="brand-subtitle">Sistema Profissional de Análise de Apostas</span>
        </div>
        <nav className="header-nav">
          <button
            className={`nav-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 Dashboard
          </button>
          <button
            className={`nav-btn ${activeTab === 'live' ? 'active' : ''}`}
            onClick={() => setActiveTab('live')}
          >
            🔴 Ao Vivo
          </button>
        </nav>
      </header>

      <main className="app-main">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'live' && <LiveBetting />}
      </main>

      <footer className="app-footer">
        <p>⚠️ Aposte com responsabilidade. Este sistema é apenas para fins informativos.</p>
      </footer>
    </div>
  );
}

export default App;
