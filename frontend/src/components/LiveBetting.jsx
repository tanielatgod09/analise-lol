import React, { useState, useEffect } from 'react';
import { getLiveOpportunities } from '../services/api';

function LiveBetting() {
  const [liveMatches, setLiveMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLive = () => {
      getLiveOpportunities()
        .then((res) => setLiveMatches(res.data))
        .catch(() => setLiveMatches([]))
        .finally(() => setLoading(false));
    };
    fetchLive();
    // Atualizar a cada 60 segundos
    const interval = setInterval(fetchLive, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
        Verificando partidas ao vivo...
      </div>
    );
  }

  return (
    <div>
      <div className="section-header">
        <h2 className="section-title">
          🔴 Live Betting
          <span className="live-badge" style={{ marginLeft: '12px' }}>
            <span className="live-dot"></span> AO VIVO
          </span>
        </h2>
        <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
          Atualização automática a cada 60 segundos
        </span>
      </div>

      {liveMatches.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📡</div>
          <p>Nenhuma partida ao vivo no momento</p>
          <p style={{ fontSize: '13px', marginTop: '8px', color: 'var(--text-muted)' }}>
            As oportunidades de apostas ao vivo aparecem aqui quando as partidas começam
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {liveMatches.map((match) => (
            <div key={match.match_id} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <div>
                  <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{match.league}</span>
                  <div style={{ fontWeight: '600', fontSize: '16px', marginTop: '4px' }}>
                    <span className="team-blue">{match.team_blue}</span>
                    <span className="vs-divider">VS</span>
                    <span className="team-red">{match.team_red}</span>
                  </div>
                </div>
                <span className="live-badge">
                  <span className="live-dot"></span> AO VIVO
                </span>
              </div>

              {match.live_opportunities && match.live_opportunities.length > 0 ? (
                <div>
                  <div style={{ fontSize: '12px', color: 'var(--color-gold)', fontWeight: '600', marginBottom: '8px' }}>
                    ⚡ {match.live_opportunities.length} OPORTUNIDADE(S) IDENTIFICADA(S)
                  </div>
                  {match.live_opportunities.map((opp, idx) => (
                    <div
                      key={idx}
                      style={{
                        background: 'rgba(0, 210, 106, 0.1)',
                        border: '1px solid var(--color-green)',
                        borderRadius: '8px',
                        padding: '10px 14px',
                        marginBottom: '8px',
                      }}
                    >
                      <div style={{ fontWeight: '600', color: 'var(--color-green)', marginBottom: '4px' }}>
                        🎯 {opp.type}
                      </div>
                      <div style={{ fontSize: '13px', display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
                        <span>{opp.bookmaker} · {opp.market} · {opp.selection}</span>
                        <span>Odd: <strong>{opp.odd?.toFixed(2)}</strong></span>
                        <span>Real: <strong>{(opp.real_probability * 100)?.toFixed(1)}%</strong></span>
                        <span>Implícita: <strong>{(opp.implied_probability * 100)?.toFixed(1)}%</strong></span>
                        <span className="ev-positive">EV: +{(opp.ev * 100)?.toFixed(2)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                  Monitorando... Nenhuma oportunidade identificada ainda
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default LiveBetting;
