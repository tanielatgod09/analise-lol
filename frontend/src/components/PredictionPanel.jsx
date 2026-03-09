import React, { useState, useEffect } from 'react';
import { getMatchAnalysis, generatePrediction } from '../services/api';

function PredictionPanel({ matchId }) {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const fetchAnalysis = () => {
    if (!matchId) return;
    setLoading(true);
    getMatchAnalysis(matchId)
      .then((res) => setAnalysis(res.data))
      .catch(() => setAnalysis(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchAnalysis();
  }, [matchId]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      await generatePrediction(matchId);
      setTimeout(fetchAnalysis, 2000);
    } catch (err) {
      console.error('Erro ao gerar previsão:', err);
    } finally {
      setGenerating(false);
    }
  };

  if (loading) return <div className="loading" style={{ padding: '20px' }}>Carregando previsões...</div>;

  const pred = analysis?.prediction;

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <div className="card-title">🤖 Previsões do Sistema</div>
        <button
          onClick={handleGenerate}
          disabled={generating}
          style={{
            background: 'rgba(74, 158, 255, 0.15)',
            border: '1px solid var(--color-blue)',
            color: 'var(--color-blue)',
            padding: '4px 12px',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '12px',
            fontFamily: 'var(--font-family)',
          }}
        >
          {generating ? '⟳ Gerando...' : '↻ Gerar Previsão'}
        </button>
      </div>

      {!pred ? (
        <div style={{ fontSize: '13px', color: 'var(--text-muted)', textAlign: 'center', padding: '12px' }}>
          Clique em "Gerar Previsão" para analisar esta partida
        </div>
      ) : (
        <div>
          {/* Probabilidades de Vitória */}
          <div style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px', fontSize: '13px' }}>
              <span className="team-blue">
                Time Azul: {(pred.blue_win_probability * 100)?.toFixed(1)}%
              </span>
              <span className="team-red">
                Time Vermelho: {(pred.red_win_probability * 100)?.toFixed(1)}%
              </span>
            </div>
            <div className="prob-bar">
              <div
                className="prob-fill-blue"
                style={{ width: `${(pred.blue_win_probability || 0) * 100}%` }}
              />
            </div>
          </div>

          {/* Previsões adicionais */}
          <div className="grid grid-3" style={{ gap: '8px', fontSize: '13px' }}>
            <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
              <div style={{ color: 'var(--text-secondary)', fontSize: '11px', marginBottom: '4px' }}>Kills Previstas</div>
              <div style={{ fontWeight: '700', fontSize: '18px' }}>
                {pred.predicted_total_kills?.toFixed(1) ?? '—'}
              </div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
              <div style={{ color: 'var(--text-secondary)', fontSize: '11px', marginBottom: '4px' }}>Duração Prev.</div>
              <div style={{ fontWeight: '700', fontSize: '18px' }}>
                {pred.predicted_duration_seconds
                  ? `${(pred.predicted_duration_seconds / 60).toFixed(0)}min`
                  : '—'}
              </div>
            </div>
            <div style={{ background: 'rgba(255,255,255,0.03)', borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
              <div style={{ color: 'var(--text-secondary)', fontSize: '11px', marginBottom: '4px' }}>Risco de Upset</div>
              <div style={{
                fontWeight: '700',
                fontSize: '18px',
                color: pred.upset_risk_score > 60 ? 'var(--color-red)' : pred.upset_risk_score > 30 ? 'var(--color-orange)' : 'var(--color-green)',
              }}>
                {pred.upset_risk_score?.toFixed(0) ?? '—'}
              </div>
            </div>
          </div>

          {/* Vantagem por fase */}
          {(pred.early_game_advantage || pred.mid_game_advantage || pred.late_game_advantage) && (
            <div style={{ marginTop: '12px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {[
                { label: 'Early', value: pred.early_game_advantage },
                { label: 'Mid', value: pred.mid_game_advantage },
                { label: 'Late', value: pred.late_game_advantage },
              ].map(({ label, value }) => (
                <div
                  key={label}
                  style={{
                    fontSize: '12px',
                    padding: '4px 10px',
                    borderRadius: '6px',
                    background: value === 'blue' ? 'rgba(74,158,255,0.15)' : value === 'red' ? 'rgba(255,74,107,0.15)' : 'rgba(255,255,255,0.05)',
                    color: value === 'blue' ? 'var(--color-blue)' : value === 'red' ? 'var(--color-red)' : 'var(--text-muted)',
                  }}
                >
                  {label}: {value === 'blue' ? '🔵' : value === 'red' ? '🔴' : '⚖️'} {value?.toUpperCase()}
                </div>
              ))}
            </div>
          )}

          {/* Confiança */}
          {pred.confidence_score != null && (
            <div style={{ marginTop: '10px', fontSize: '12px', color: 'var(--text-muted)' }}>
              Confiança do modelo: {(pred.confidence_score * 100).toFixed(0)}%
              {pred.monte_carlo_simulations && ` | ${pred.monte_carlo_simulations.toLocaleString()} simulações Monte Carlo`}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default PredictionPanel;
