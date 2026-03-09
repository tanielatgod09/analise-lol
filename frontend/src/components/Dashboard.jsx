import React, { useState, useEffect } from 'react';
import { getDashboard, getHighlightedBets } from '../services/api';
import MatchCard from './MatchCard';
import BetRecommendations from './BetRecommendations';

function Dashboard() {
  const [data, setData] = useState(null);
  const [highlightedBets, setHighlightedBets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [dashRes, betsRes] = await Promise.all([
          getDashboard(),
          getHighlightedBets(0.75),
        ]);
        setData(dashRes.data);
        setHighlightedBets(betsRes.data);
      } catch (err) {
        setError('Erro ao carregar dados. Verifique se o backend está rodando.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    // Atualizar a cada 5 minutos
    const interval = setInterval(fetchData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
        Carregando dados...
      </div>
    );
  }

  if (error) {
    return (
      <div className="empty-state">
        <div className="empty-icon">⚠️</div>
        <p>{error}</p>
      </div>
    );
  }

  const resumo = data?.resumo || {};
  const partidas = data?.partidas_hoje || [];
  const destaques = data?.apostas_em_destaque || [];

  return (
    <div>
      {/* --- Resumo --- */}
      <div className="section-header">
        <h2 className="section-title">📊 Dashboard</h2>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
          Atualizado: {data?.atualizado_em ? new Date(data.atualizado_em).toLocaleString('pt-BR') : '—'}
        </span>
      </div>

      <div className="grid grid-4" style={{ marginBottom: '24px' }}>
        <div className="card">
          <div className="card-title">Partidas Hoje</div>
          <div style={{ fontSize: '32px', fontWeight: '700', color: 'var(--color-blue)' }}>
            {resumo.partidas_hoje ?? '—'}
          </div>
        </div>
        <div className="card">
          <div className="card-title">Ao Vivo</div>
          <div style={{ fontSize: '32px', fontWeight: '700', color: 'var(--color-red)' }}>
            {resumo.partidas_ao_vivo ?? '—'}
          </div>
        </div>
        <div className="card">
          <div className="card-title">Apostas em Destaque</div>
          <div style={{ fontSize: '32px', fontWeight: '700', color: 'var(--color-gold)' }}>
            {resumo.apostas_em_destaque ?? '—'}
          </div>
        </div>
        <div className="card">
          <div className="card-title">Times Monitorados</div>
          <div style={{ fontSize: '32px', fontWeight: '700', color: 'var(--color-green)' }}>
            {resumo.total_times ?? '—'}
          </div>
        </div>
      </div>

      {/* --- Apostas em Destaque --- */}
      {destaques.length > 0 && (
        <div style={{ marginBottom: '24px' }}>
          <div className="section-header">
            <h3 className="section-title">⭐ Apostas em Destaque</h3>
          </div>
          <BetRecommendations bets={destaques} />
        </div>
      )}

      {/* --- Partidas do Dia --- */}
      <div className="section-header">
        <h3 className="section-title">🗓️ Partidas de Hoje</h3>
      </div>

      {partidas.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📅</div>
          <p>Nenhuma partida agendada para hoje</p>
        </div>
      ) : (
        <div className="grid grid-2">
          {partidas.map((match) => (
            <MatchCard key={match.id} match={match} />
          ))}
        </div>
      )}
    </div>
  );
}

export default Dashboard;
