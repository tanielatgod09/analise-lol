import React from 'react';

function DraftAnalysis({ draftData }) {
  if (!draftData) {
    return (
      <div style={{ fontSize: '13px', color: 'var(--text-muted)', textAlign: 'center', padding: '12px' }}>
        Dados do draft não disponíveis
      </div>
    );
  }

  const blue = draftData.blue_team || {};
  const red = draftData.red_team || {};
  const advantageTeam = draftData.draft_advantage_team;

  return (
    <div>
      <div className="card-title">🎮 Análise do Draft</div>
      <div className="grid grid-2" style={{ gap: '12px' }}>
        {/* Time Azul */}
        <div style={{ background: 'rgba(74, 158, 255, 0.05)', borderRadius: '8px', padding: '12px', border: '1px solid rgba(74,158,255,0.2)' }}>
          <div style={{ color: 'var(--color-blue)', fontWeight: '600', marginBottom: '8px', fontSize: '13px' }}>
            🔵 Time Azul
          </div>
          <div style={{ marginBottom: '6px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>PICKS: </span>
            <span style={{ fontSize: '13px' }}>{(blue.picks || []).join(', ') || '—'}</span>
          </div>
          <div style={{ marginBottom: '6px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>BANS: </span>
            <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{(blue.bans || []).join(', ') || '—'}</span>
          </div>
          <div style={{ display: 'flex', gap: '8px', marginTop: '8px', flexWrap: 'wrap' }}>
            {blue.composition_style && (
              <span style={{ fontSize: '11px', background: 'rgba(74,158,255,0.15)', color: 'var(--color-blue)', padding: '2px 8px', borderRadius: '10px' }}>
                {blue.composition_style}
              </span>
            )}
            {blue.meta_score != null && (
              <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                Meta: {(blue.meta_score * 100).toFixed(0)}%
              </span>
            )}
          </div>
        </div>

        {/* Time Vermelho */}
        <div style={{ background: 'rgba(255, 74, 107, 0.05)', borderRadius: '8px', padding: '12px', border: '1px solid rgba(255,74,107,0.2)' }}>
          <div style={{ color: 'var(--color-red)', fontWeight: '600', marginBottom: '8px', fontSize: '13px' }}>
            🔴 Time Vermelho
          </div>
          <div style={{ marginBottom: '6px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>PICKS: </span>
            <span style={{ fontSize: '13px' }}>{(red.picks || []).join(', ') || '—'}</span>
          </div>
          <div style={{ marginBottom: '6px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>BANS: </span>
            <span style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{(red.bans || []).join(', ') || '—'}</span>
          </div>
          <div style={{ display: 'flex', gap: '8px', marginTop: '8px', flexWrap: 'wrap' }}>
            {red.composition_style && (
              <span style={{ fontSize: '11px', background: 'rgba(255,74,107,0.15)', color: 'var(--color-red)', padding: '2px 8px', borderRadius: '10px' }}>
                {red.composition_style}
              </span>
            )}
            {red.meta_score != null && (
              <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                Meta: {(red.meta_score * 100).toFixed(0)}%
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Resultado */}
      {advantageTeam && (
        <div style={{
          marginTop: '12px',
          textAlign: 'center',
          fontSize: '14px',
          fontWeight: '600',
          color: advantageTeam === 'blue' ? 'var(--color-blue)' : advantageTeam === 'red' ? 'var(--color-red)' : 'var(--text-secondary)',
        }}>
          Vantagem no Draft:{' '}
          {advantageTeam === 'blue' ? '🔵 Time Azul' : advantageTeam === 'red' ? '🔴 Time Vermelho' : '⚖️ Equilibrado'}
          {draftData.draft_advantage_score != null && (
            <span style={{ fontSize: '12px', marginLeft: '8px', color: 'var(--text-secondary)' }}>
              ({(draftData.draft_advantage_score * 100).toFixed(1)}%)
            </span>
          )}
        </div>
      )}
    </div>
  );
}

export default DraftAnalysis;
