import React from 'react';

const CLASSIFICATION_LABELS = {
  muito_segura: { label: 'Muito Segura', cls: 'badge-muito-segura' },
  boa: { label: 'Boa', cls: 'badge-boa' },
  moderada: { label: 'Moderada', cls: 'badge-moderada' },
  arriscada: { label: 'Arriscada', cls: 'badge-arriscada' },
};

function BetRecommendations({ bets }) {
  if (!bets || bets.length === 0) {
    return (
      <div className="empty-state" style={{ padding: '20px' }}>
        <div className="empty-icon">🎯</div>
        <p>Nenhuma aposta recomendada no momento</p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      {bets.map((bet) => {
        const classInfo = CLASSIFICATION_LABELS[bet.classificacao || bet.classification] || {
          label: bet.classificacao || bet.classification || '—',
          cls: 'badge-moderada',
        };
        const ev = bet.ev ?? bet.expected_value;
        const evClass = ev > 0 ? 'ev-positive' : ev < 0 ? 'ev-negative' : 'ev-neutral';

        return (
          <div
            key={bet.id}
            className={`card ${bet.is_highlighted ? 'highlighted' : ''}`}
            style={{ padding: '14px 18px' }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px' }}>
              <div>
                <div style={{ fontWeight: '600', fontSize: '15px', marginBottom: '4px' }}>
                  {bet.mercado || bet.market} — {bet.selecao || bet.selection}
                </div>
                <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                  {bet.casa || bet.bookmaker} · Odd: <strong style={{ color: 'var(--text-primary)' }}>
                    {(bet.odd || bet.odd_value)?.toFixed(2)}
                  </strong>
                </div>
              </div>
              <span className={`badge ${classInfo.cls}`}>{classInfo.label}</span>
            </div>

            <div style={{ marginTop: '10px', display: 'flex', gap: '20px', fontSize: '13px', flexWrap: 'wrap' }}>
              <div>
                <span style={{ color: 'var(--text-secondary)' }}>Prob. Real: </span>
                <strong>{((bet.probabilidade_real || bet.real_probability || 0) * 100).toFixed(1)}%</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-secondary)' }}>Prob. Implícita: </span>
                <strong>{((bet.implied_probability || 0) * 100).toFixed(1)}%</strong>
              </div>
              <div>
                <span style={{ color: 'var(--text-secondary)' }}>EV: </span>
                <strong className={evClass}>{ev > 0 ? '+' : ''}{(ev * 100).toFixed(2)}%</strong>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default BetRecommendations;
