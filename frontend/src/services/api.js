import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para tratamento de erros
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('Erro na API:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ------------------- Dashboard -------------------

export const getDashboard = () => api.get('/dashboard/');

export const getGlobalStats = () => api.get('/dashboard/stats');

// ------------------- Partidas -------------------

export const getUpcomingMatches = (league = null, hoursAhead = 48) => {
  const params = { hours_ahead: hoursAhead };
  if (league) params.league = league;
  return api.get('/matches/upcoming', { params });
};

export const getLiveMatches = () => api.get('/matches/live');

export const getMatchDetails = (matchId) => api.get(`/matches/${matchId}`);

// ------------------- Times -------------------

export const getTeams = (league = null) => {
  const params = {};
  if (league) params.league = league;
  return api.get('/teams/', { params });
};

export const getTeamStats = (teamId) => api.get(`/teams/${teamId}/stats`);

// ------------------- Jogadores -------------------

export const getPlayers = (role = null, teamId = null) => {
  const params = {};
  if (role) params.role = role;
  if (teamId) params.team_id = teamId;
  return api.get('/players/', { params });
};

// ------------------- Previsões -------------------

export const getMatchAnalysis = (matchId) =>
  api.get(`/predictions/match/${matchId}`);

export const generatePrediction = (matchId) =>
  api.post(`/predictions/match/${matchId}/generate`);

export const getHighlightedBets = (minConfidence = 0.75) =>
  api.get('/predictions/highlighted', { params: { min_confidence: minConfidence } });

// ------------------- Odds -------------------

export const getMatchOdds = (matchId) => api.get(`/odds/match/${matchId}`);

export const getOddsComparison = (matchId, market = null) => {
  const params = {};
  if (market) params.market = market;
  return api.get(`/odds/match/${matchId}/comparison`, { params });
};

// ------------------- Live Betting -------------------

export const getLiveOpportunities = () => api.get('/live/matches');

export const updateLiveProbabilities = (matchId, gameState) =>
  api.post(`/live/update/${matchId}`, gameState);

export default api;
