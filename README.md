# ⚔️ Sistema Profissional de Análise de Apostas para League of Legends

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue.svg)](https://reactjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://postgresql.org)

Sistema profissional completo de análise de apostas para partidas de League of Legends esports.
Utiliza dados reais de APIs confiáveis, modelos estatísticos avançados e machine learning para
identificar apostas com valor esperado positivo (EV+).

> ⚠️ **Aviso importante**: Este sistema é destinado exclusivamente a fins informativos e analíticos.
> Aposte com responsabilidade. O jogo pode causar dependência.

---

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Ligas Analisadas](#-ligas-analisadas)
- [Arquitetura](#-arquitetura)
- [Tecnologias](#-tecnologias)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Execução](#-execução)
- [APIs Utilizadas](#-apis-utilizadas)
- [Modelos de Machine Learning](#-modelos-de-machine-learning)
- [Análises Disponíveis](#-análises-disponíveis)
- [Mercados de Apostas](#-mercados-de-apostas)
- [Classificação das Apostas](#-classificação-das-apostas)

---

## ✨ Funcionalidades

### 📊 Coleta de Dados
- Coleta automática de dados de partidas via **PandaScore API**, **LoL Esports API** e **Oracle's Elixir**
- **Rastreamento de line-ups**: apenas estatísticas com a formação atual de cada time
- Atualização automática a cada **5 minutos** via APScheduler
- Histórico de confrontos diretos (H2H) com filtro de line-up

### 🎯 Previsões
- **Probabilidade de vitória** usando ensemble de modelos estatísticos e ML
- **Over/Under kills** com distribuição de Poisson adaptada para LoL
- **Duração da partida** (curto, médio, longo)
- **Objetivos** (dragões, barões, torres por time)
- **Vantagem por fase** (early, mid, late game)

### 💰 Análise de Apostas
- **Expected Value (EV)** calculado para cada odd disponível
- **Critério de Kelly** para dimensionamento de apostas
- **Comparação de odds** entre múltiplas casas de apostas
- Destaque automático de apostas com probabilidade > 75%

### 🔴 Live Betting
- Atualização de probabilidades em **tempo real** durante as partidas
- Modelo dinâmico baseado em: gold, kills, dragões, barões, torres e visão
- Detecção automática de **oportunidades de apostas ao vivo**

### 🎮 Análises Avançadas
- **Análise do Draft**: picks, bans, counters, sinergia, meta do patch
- **Estilo de jogo**: Early/Mid/Late Game Team
- **Ritmo**: muito agressivo, agressivo, equilibrado, lento
- **Matchups de lane**: comparação top, jungle, mid, bot, suporte
- **Detecção de Upsets**: Upset Risk Score (0–100)
- **Análise de patch/meta**: campeões mais fortes, banidos, winrate

---

## 🌍 Ligas Analisadas

| Liga | Região | Descrição |
|------|--------|-----------|
| **LCK** | Coreia | League of Legends Champions Korea |
| **LEC** | Europa | LoL EMEA Championship |
| **LCS** | América do Norte | League Championship Series |
| **CBLOL** | Brasil | Campeonato Brasileiro de LoL |
| **LPL** | China | League of Legends Pro League |
| **MSI** | Internacional | Mid-Season Invitational |
| **Worlds** | Internacional | Campeonato Mundial |

---

## 🏗️ Arquitetura

```
analise-lol/
├── backend/                    # API Python + FastAPI
│   ├── main.py                 # Ponto de entrada FastAPI
│   ├── config.py               # Configurações e variáveis de ambiente
│   ├── database.py             # Conexão PostgreSQL via SQLAlchemy
│   ├── models/                 # Modelos ORM (team, player, match, odds, etc.)
│   ├── schemas/                # Schemas Pydantic para validação
│   ├── api/routes/             # Rotas da API REST
│   ├── services/               # Lógica de negócio
│   │   ├── data_collector.py   # Coleta dados de APIs externas
│   │   ├── odds_collector.py   # Coleta odds de casas de apostas
│   │   ├── lineup_tracker.py   # Rastreia line-ups atuais
│   │   ├── probability_engine.py # Motor de probabilidades
│   │   ├── monte_carlo.py      # Simulação Monte Carlo (10.000+)
│   │   ├── ev_calculator.py    # Cálculo de EV e Kelly
│   │   ├── draft_analyzer.py   # Análise de draft
│   │   ├── upset_detector.py   # Detecção de upsets
│   │   ├── live_betting.py     # Probabilidades dinâmicas ao vivo
│   │   └── bet_recommender.py  # Recomendações de apostas
│   ├── ml/                     # Machine Learning
│   │   ├── models/             # Win, Kills, Duration, Objectives predictors
│   │   ├── feature_engineering.py
│   │   ├── model_trainer.py
│   │   └── predictor.py
│   ├── tasks/                  # Scheduler e tarefas automáticas
│   └── utils/                  # Logger, validators, constants
├── frontend/                   # Dashboard React
│   └── src/
│       ├── components/         # Dashboard, MatchCard, PredictionPanel, etc.
│       └── services/api.js     # Integração com o backend
├── tests/                      # Testes automatizados
├── alembic/                    # Migrações do banco de dados
├── docker-compose.yml          # Infraestrutura Docker
└── requirements.txt            # Dependências Python
```

---

## 🛠️ Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| **Backend** | Python 3.11, FastAPI, Uvicorn |
| **Banco de Dados** | PostgreSQL 16, SQLAlchemy 2.0, Alembic |
| **Machine Learning** | Scikit-learn, XGBoost, LightGBM, SciPy |
| **Dados** | Pandas, NumPy |
| **Scheduler** | APScheduler |
| **Frontend** | React 18, Chart.js |
| **Infraestrutura** | Docker, Docker Compose |
| **Logs** | Structlog (JSON estruturado) |

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.11+
- PostgreSQL 16+
- Node.js 20+ (para o frontend)
- Docker e Docker Compose (opcional)

### 1. Clonar o repositório

```bash
git clone https://github.com/tanielatgod09/analise-lol.git
cd analise-lol
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Editar .env com suas chaves de API
```

### 3. Instalar dependências Python

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 4. Configurar banco de dados

```bash
# Criar banco de dados PostgreSQL
createdb analise_lol

# Executar migrações
alembic upgrade head
```

### 5. Instalar dependências do frontend

```bash
cd frontend
npm install
cd ..
```

---

## ⚙️ Configuração

Edite o arquivo `.env` com suas configurações:

```env
# Banco de Dados
DATABASE_URL=postgresql://postgres:senha@localhost:5432/analise_lol

# APIs de Dados (obrigatório para coleta automática)
PANDASCORE_API_KEY=seu_token_aqui     # https://developers.pandascore.co/
RIOT_API_KEY=RGAPI-xxxxx              # https://developer.riotgames.com/

# Odds (para coleta de odds)
ODDS_API_KEY=sua_chave_aqui           # https://the-odds-api.com/

# A chave da LoL Esports API é pública
LOL_ESPORTS_API_KEY=0TvQnueqKa5mxJntVWt0w4LpLfEkrV1Ta8rQBb9Z
```

### Obtenção das chaves de API

| API | URL | Custo |
|-----|-----|-------|
| PandaScore | https://developers.pandascore.co/ | Gratuito (limitado) / Pago |
| Riot Games | https://developer.riotgames.com/ | Gratuito |
| TheOddsAPI | https://the-odds-api.com/ | Gratuito (500 req/mês) / Pago |
| LoL Esports | Chave pública disponível no `.env.example` | Gratuito |

---

## ▶️ Execução

### Com Docker (recomendado)

```bash
# Iniciar todos os serviços
docker-compose up -d

# Verificar logs
docker-compose logs -f backend

# Parar serviços
docker-compose down
```

### Sem Docker

#### Backend

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Executar migrações
alembic upgrade head

# Iniciar servidor
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend
npm start
```

### Acessos

| Serviço | URL |
|---------|-----|
| **API Backend** | http://localhost:8000 |
| **Documentação Swagger** | http://localhost:8000/docs |
| **Frontend Dashboard** | http://localhost:3000 |
| **Health Check** | http://localhost:8000/health |

---

## 🔌 APIs Utilizadas

### Endpoints da API Backend

#### Partidas
```
GET /api/v1/matches/upcoming          # Partidas agendadas
GET /api/v1/matches/live              # Partidas ao vivo
GET /api/v1/matches/{id}              # Detalhes de uma partida
```

#### Times
```
GET /api/v1/teams/                    # Listar times
GET /api/v1/teams/{id}/stats          # Estatísticas detalhadas
```

#### Previsões
```
GET /api/v1/predictions/match/{id}    # Análise completa da partida
POST /api/v1/predictions/match/{id}/generate  # Gerar previsões
GET /api/v1/predictions/highlighted   # Apostas em destaque (prob > 75%)
```

#### Odds
```
GET /api/v1/odds/match/{id}           # Odds de uma partida
GET /api/v1/odds/match/{id}/comparison # Comparação entre casas
```

#### Live Betting
```
GET /api/v1/live/matches              # Oportunidades ao vivo
POST /api/v1/live/update/{id}         # Atualizar probabilidades ao vivo
```

#### Dashboard
```
GET /api/v1/dashboard/                # Resumo do dashboard
GET /api/v1/dashboard/stats           # Estatísticas globais
```

---

## 🤖 Modelos de Machine Learning

### Preditor de Vitória (WinPredictor)
- **Regressão Logística**: baseline interpretável
- **XGBoost**: gradient boosting com alta precisão
- **LightGBM**: gradient boosting otimizado para velocidade
- Avaliado por **ROC-AUC** e **Brier Score**
- **Calibração verificada** para garantir probabilidades confiáveis

### Preditor de Kills (KillsPredictor)
- Regressão de **Poisson** — distribuição correta para contagem de eventos
- Calcula probabilidade de **over/under** para limiares: 15.5, 20.5, 22.5, 25.5, 27.5, 30.5, 35.5

### Preditor de Duração (DurationPredictor)
- **Gradient Boosting Regressor**
- Classifica partidas como: **jogo curto** (<27min), **jogo médio** (<34min), **jogo longo** (>34min)

### Modelo Bayesiano (BayesianModel)
- Prior Beta para modelar probabilidade de vitória
- Atualização incremental com novas evidências
- Intervalo de credibilidade 95% para quantificar incerteza

### Features Utilizadas
- Winrate (e diferença de winrate)
- Kills, mortes por jogo (e diferenças)
- Gold por minuto
- First blood/dragon/baron rate
- Torres por jogo
- Duração média das partidas
- Número de jogos com a line-up atual

---

## 📈 Análises Disponíveis

### Simulação Monte Carlo
- **10.000+ simulações** por partida
- Distribuições de probabilidade robustas
- Over/under com múltiplos limiares

### Detecção de Upsets (Upset Risk Score 0–100)
| Score | Classificação | Impacto nas Apostas |
|-------|--------------|---------------------|
| 0–30 | Risco baixo | Nenhum |
| 30–60 | Risco moderado | Redução de 10% na confiança |
| 60–100 | Alto risco | Redução de 20% na confiança |

### Análise de Draft
1. Identificação dos campeões escolhidos
2. Análise de counters
3. Score de sinergia da composição
4. Alinhamento com o meta do patch
5. Conforto dos jogadores com os campeões

### Live Betting — Fatores Considerados
| Fator | Peso |
|-------|------|
| Diferença de Gold | 35% |
| Diferença de Kills | 20% |
| Diferença de Dragões | 15% |
| Diferença de Barões | 15% |
| Diferença de Torres | 10% |
| Tempo de Jogo | 5% |

---

## 💹 Mercados de Apostas

| Mercado | Descrição |
|---------|-----------|
| `match_winner` | Vencedor da partida |
| `first_blood` | Primeiro abate |
| `first_dragon` | Primeiro dragão |
| `first_baron` | Primeiro barão |
| `over_kills` | Mais de X kills totais |
| `under_kills` | Menos de X kills totais |
| `total_dragons` | Total de dragões |
| `total_barons` | Total de barões |
| `total_towers` | Total de torres destruídas |
| `kills_handicap` | Handicap de kills |
| `map_winner` | Vencedor do mapa (em séries) |

---

## 🏆 Classificação das Apostas

| Classificação | Probabilidade | Destaque |
|---------------|--------------|---------|
| ⭐ **Muito Segura** | > 85% | ✅ Sim |
| ✅ **Boa** | 75% – 85% | ✅ Sim |
| ⚠️ **Moderada** | 65% – 75% | ❌ Não |
| ❌ **Arriscada** | < 65% | ❌ Não |

> Apenas apostas com **probabilidade > 75% e EV > 0** são destacadas no dashboard.

---

## 🧪 Testes

```bash
# Executar todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ -v --cov=backend --cov-report=html

# Testes específicos
pytest tests/test_ev_calculator.py -v
pytest tests/test_monte_carlo.py -v
pytest tests/test_ml_models.py -v
```

---

## 📐 Fórmulas Matemáticas

### Expected Value (EV)
```
EV = (probabilidade_real × odd) - 1
```

### Probabilidade Implícita
```
probabilidade_implícita = 1 / odd
```

### Critério de Kelly (Fracionado 25%)
```
Kelly = 0.25 × [(b × p - q) / b]
onde: b = odd - 1, p = prob_real, q = 1 - p
```

### Distribuição de Poisson (Kills)
```
P(X = k) = (λᵏ × e⁻λ) / k!
onde: λ = kills médios por jogo
```

---

## 🗂️ Estrutura do Banco de Dados

| Tabela | Descrição |
|--------|-----------|
| `teams` | Times profissionais com estatísticas da line-up atual |
| `players` | Jogadores com KDA, pool de campeões |
| `matches` | Partidas com resultado, draft, estatísticas |
| `champions` | Campeões com stats por patch |
| `odds` | Odds coletadas de casas de apostas |
| `predictions` | Previsões geradas pelo sistema |
| `bet_recommendations` | Recomendações de apostas com EV calculado |

---

## 🔒 Segurança

- Validação rigorosa de dados em todas as entradas
- Logs estruturados em JSON para auditoria
- Tratamento robusto de erros em todos os módulos
- Variáveis sensíveis apenas via `.env` (nunca no código)
- Verificação de inconsistências nos dados

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## ⚠️ Responsabilidade

Este sistema fornece análises estatísticas e probabilísticas baseadas em dados históricos.
**Resultados passados não garantem resultados futuros.** Use com responsabilidade e nunca aposte
valores que não pode perder.

**Se o jogo estiver prejudicando sua vida, ligue:** Jogo Responsável: 0800 722 2365
