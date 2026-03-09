import React from 'react';

function TeamStats({ team }) {
  if (!team) return null;

  const statItems = [
    { label: 'Winrate', value: team.winrate != null ? `${(team.winrate * 100).toFixed(1)}%` : '—', color: team.winrate > 0.5 ? 'var(--color-green)' : 'var(--color-red)' },
    { label: 'Jogos (Lineup Atual)', value: team.games_played ?? '—' },
    { label: 'Kills/Jogo', value: team.kills_per_game?.toFixed(1) ?? '—' },
    { label: 'Mortes/Jogo', value: team.deaths_per_game?.toFixed(1) ?? '—' },
    { label: 'Gold/Min', value: team.gold_per_minute ? `${(team.gold_per_minute / 1000).toFixed(1)}k` : '—' },
    { label: 'First Blood%', value: team.first_blood_rate != null ? `${(team.first_blood_rate * 100).toFixed(0)}%` : '—' },
    { label: 'First Dragon%', value: team.first_dragon_rate != null ? `${(team.first_dragon_rate * 100).toFixed(0)}%` : '—' },
    { label: 'First Baron%', value: team.first_baron_rate != null ? `${(team.first_baron_rate * 100).toFixed(0)}%` : '—' },
    { label: 'Torres/Jogo', value: team.towers_per_game?.toFixed(1) ?? '—' },
    { label: 'Duração Média', value: team.avg_game_duration ? `${Math.round(team.avg_game_duration / 60)}min` : '—' },
  ];

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div>
          <h3 style={{ fontSize: '18px', fontWeight: '700' }}>{team.name}</h3>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>{team.league}</div>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {team.playstyle && (
            <span style={{ background: 'rgba(74,158,255,0.15)', color: 'var(--color-blue)', padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: '600' }}>
              {team.playstyle?.replace('_', ' ').toUpperCase()}
            </span>
          )}
          {team.game_pace && (
            <span style={{ background: 'rgba(255,140,0,0.15)', color: 'var(--color-orange)', padding: '3px 10px', borderRadius: '20px', fontSize: '11px', fontWeight: '600' }}>
              {team.game_pace?.replace('_', ' ').toUpperCase()}
            </span>
          )}
        </div>
      </div>

      {team.current_lineup_since && (
        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '12px' }}>
          Line-up atual desde: {new Date(team.current_lineup_since).toLocaleDateString('pt-BR')}
        </div>
      )}

      <div className="grid grid-3" style={{ gap: '8px' }}>
        {statItems.map(({ label, value, color }) => (
          <div
            key={label}
            style={{ background: 'rgba(255,255,255,0.03)', borderRadius: '8px', padding: '10px', textAlign: 'center' }}
          >
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginBottom: '4px' }}>{label}</div>
            <div style={{ fontWeight: '700', fontSize: '16px', color: color || 'var(--text-primary)' }}>{value}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default TeamStats;
