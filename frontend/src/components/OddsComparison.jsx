import React, { useState, useEffect } from 'react';
import { getOddsComparison } from '../services/api';

function OddsComparison({ matchId }) {
  const [oddsData, setOddsData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!matchId) return;
    getOddsComparison(matchId)
      .then((res) => setOddsData(res.data))
      .catch(() => setOddsData([]))
      .finally(() => setLoading(false));
  }, [matchId]);

  if (loading) return <div className="loading" style={{ padding: '20px' }}>Carregando odds...</div>;

  if (oddsData.length === 0) {
    return (
      <div style={{ fontSize: '13px', color: 'var(--text-muted)', textAlign: 'center', padding: '16px' }}>
        Nenhuma odd disponível
      </div>
    );
  }

  return (
    <div>
      <div className="card-title">🏦 Odds por Casa de Apostas</div>
      {oddsData.map((market, idx) => (
        <div key={idx} style={{ marginBottom: '12px' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '6px' }}>
            {market.market} — <strong style={{ color: 'var(--text-primary)' }}>{market.selection}</strong>
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {(market.bookmakers || []).map((bk, i) => (
              <div
                key={i}
                style={{
                  background: bk.bookmaker === market.best_bookmaker ? 'rgba(74, 158, 255, 0.15)' : 'rgba(255,255,255,0.05)',
                  border: `1px solid ${bk.bookmaker === market.best_bookmaker ? 'var(--color-blue)' : 'var(--border-color)'}`,
                  borderRadius: '8px',
                  padding: '6px 12px',
                  fontSize: '13px',
                }}
              >
                <div style={{ color: 'var(--text-secondary)', fontSize: '11px' }}>{bk.bookmaker}</div>
                <div style={{ fontWeight: '700', color: bk.bookmaker === market.best_bookmaker ? 'var(--color-blue)' : 'var(--text-primary)' }}>
                  {bk.odd?.toFixed(2)}
                </div>
                <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                  {(bk.implied_prob * 100)?.toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

export default OddsComparison;
