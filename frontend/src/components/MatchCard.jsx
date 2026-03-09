import React, { useState } from 'react';
import PredictionPanel from './PredictionPanel';
import OddsComparison from './OddsComparison';

function MatchCard({ match }) {
  const [showDetails, setShowDetails] = useState(false);

  const horario = match.scheduled_at
    ? new Date(match.scheduled_at).toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit',
      })
    : '—';

  const isLive = match.status === 'running';

  return (
    <div className={`card ${showDetails ? 'highlighted' : ''}`}
      style={{ cursor: 'pointer' }}
      onClick={() => setShowDetails(!showDetails)}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <span style={{ fontSize: '11px', color: 'var(--text-secondary)', fontWeight: '600' }}>
          {match.liga || match.league}
        </span>
        {isLive ? (
          <span className="live-badge">
            <span className="live-dot"></span> AO VIVO
          </span>
        ) : (
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{horario}</span>
        )}
      </div>

      {/* Times */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 0' }}>
        <span className="team-blue" style={{ fontWeight: '600', fontSize: '16px' }}>
          {match.time_azul || match.blue_team_name || 'Time Azul'}
        </span>
        <span className="vs-divider">VS</span>
        <span className="team-red" style={{ fontWeight: '600', fontSize: '16px' }}>
          {match.time_vermelho || match.red_team_name || 'Time Vermelho'}
        </span>
      </div>

      {/* Detalhes expandidos */}
      {showDetails && (
        <div style={{ marginTop: '16px', borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}
          onClick={(e) => e.stopPropagation()}
        >
          <PredictionPanel matchId={match.id} />
          <div style={{ marginTop: '12px' }}>
            <OddsComparison matchId={match.id} />
          </div>
        </div>
      )}

      {!showDetails && (
        <div style={{ marginTop: '8px', fontSize: '12px', color: 'var(--text-muted)', textAlign: 'center' }}>
          Clique para ver análise completa ▾
        </div>
      )}
    </div>
  );
}

export default MatchCard;
