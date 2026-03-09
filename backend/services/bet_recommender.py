"""
Serviço de Recomendação de Apostas.

Orquestra todos os serviços para gerar recomendações completas
para uma partida, incluindo previsões ML e análise de EV.
"""
from datetime import datetime
from sqlalchemy.orm import Session

from backend.models.match import Match
from backend.models.odds import Odds
from backend.models.prediction import Prediction
from backend.models.bet_recommendation import BetRecommendation
from backend.models.team import Team
from backend.services.probability_engine import ProbabilityEngine
from backend.services.monte_carlo import MonteCarloSimulator
from backend.services.ev_calculator import EVCalculator
from backend.services.upset_detector import UpsetDetector
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class BetRecommender:
    """
    Orquestra a geração de previsões e recomendações de apostas
    para uma partida de League of Legends.
    """

    def __init__(self, db: Session):
        self.db = db
        self.prob_engine = ProbabilityEngine(db)
        self.monte_carlo = MonteCarloSimulator()
        self.ev_calc = EVCalculator()
        self.upset_detector = UpsetDetector(db)

    def generate_recommendations(self, match_id: int) -> Prediction:
        """
        Gerar previsões completas e recomendações de apostas para uma partida.

        Fluxo:
        1. Calcular probabilidades de vitória
        2. Executar Monte Carlo (10.000+ simulações)
        3. Calcular risco de upset
        4. Para cada odd disponível, calcular EV
        5. Salvar previsão e recomendações no banco
        """
        match = self.db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise ValueError(f"Partida {match_id} não encontrada")

        blue_team = self.db.query(Team).filter(Team.id == match.team_blue_id).first()
        red_team = self.db.query(Team).filter(Team.id == match.team_red_id).first()

        if not blue_team or not red_team:
            raise ValueError(f"Times não encontrados para a partida {match_id}")

        # 1. Calcular probabilidades de vitória
        win_probs = self.prob_engine.calculate_win_probability(match)
        blue_win_prob = win_probs["blue_win_prob"]
        red_win_prob = win_probs["red_win_prob"]

        # 2. Simular via Monte Carlo
        blue_kills_avg = blue_team.kills_per_game or 12.0
        red_kills_avg = red_team.kills_per_game or 12.0
        duration_avg = (blue_team.avg_game_duration or 0 + red_team.avg_game_duration or 0) / 2 or 1900

        mc_results = self.monte_carlo.simulate_match(
            blue_win_prob=blue_win_prob,
            blue_kills_avg=blue_kills_avg,
            red_kills_avg=red_kills_avg,
            duration_avg=duration_avg,
        )

        # Modelo Poisson para kills
        poisson_results = self.monte_carlo.calculate_poisson_kills(
            lambda_blue=blue_kills_avg,
            lambda_red=red_kills_avg,
        )

        # 3. Vantagem por fase
        phase_adv = self.prob_engine.calculate_phase_advantage(blue_team, red_team)

        # 4. Risco de upset
        predicted_winner_id = match.team_blue_id if blue_win_prob > 0.5 else match.team_red_id
        upset_risk = self.upset_detector.calculate_upset_risk(
            match, predicted_winner_id, max(blue_win_prob, red_win_prob)
        )

        # Reduzir confiança se risco de upset alto
        confidence = win_probs["confidence"] * (1 - upset_risk["confidence_reduction"])

        # 5. Salvar previsão
        prediction = Prediction(
            match_id=match_id,
            blue_win_probability=round(blue_win_prob, 4),
            red_win_probability=round(red_win_prob, 4),
            predicted_total_kills=mc_results["kills"]["total_avg"],
            kills_std_dev=mc_results["kills"]["total_std"],
            predicted_duration_seconds=mc_results["duration"]["avg_seconds"],
            early_game_advantage=phase_adv["early"],
            mid_game_advantage=phase_adv["mid"],
            late_game_advantage=phase_adv["late"],
            upset_risk_score=upset_risk["upset_risk_score"],
            confidence_score=round(confidence, 4),
            model_used="statistical_composite",
            monte_carlo_simulations=self.monte_carlo.n_simulations,
            detailed_results={
                "monte_carlo": mc_results,
                "poisson": poisson_results,
                "win_probability_factors": win_probs["factors"],
                "upset_risk": upset_risk,
                "phase_advantage": phase_adv,
            },
        )
        self.db.add(prediction)
        self.db.flush()  # Para obter o ID antes do commit

        # 6. Gerar recomendações para cada odd disponível
        odds_list = self.db.query(Odds).filter(Odds.match_id == match_id).all()
        recommendations = self._generate_bet_recommendations(
            match=match,
            prediction=prediction,
            odds_list=odds_list,
            blue_win_prob=blue_win_prob,
            red_win_prob=red_win_prob,
            mc_results=mc_results,
            poisson_results=poisson_results,
        )

        for rec in recommendations:
            self.db.add(rec)

        self.db.commit()
        logger.info(
            f"Partida {match_id}: {len(recommendations)} apostas recomendadas geradas"
        )
        return prediction

    def _generate_bet_recommendations(
        self,
        match: Match,
        prediction: Prediction,
        odds_list: list,
        blue_win_prob: float,
        red_win_prob: float,
        mc_results: dict,
        poisson_results: dict,
    ) -> list[BetRecommendation]:
        """Gerar recomendações de apostas para todos os mercados disponíveis."""
        recommendations = []

        for odd_entry in odds_list:
            real_prob = self._get_real_probability_for_market(
                odd_entry.market,
                odd_entry.selection,
                match,
                blue_win_prob,
                red_win_prob,
                mc_results,
                poisson_results,
            )

            if real_prob is None:
                continue

            ev = self.ev_calc.calculate_ev(real_prob, odd_entry.odd_value)
            implied = self.ev_calc.calculate_implied_probability(odd_entry.odd_value)
            classification = self.ev_calc.classify_bet(real_prob)
            highlighted = self.ev_calc.is_highlighted(real_prob)

            rec = BetRecommendation(
                match_id=match.id,
                prediction_id=prediction.id,
                market=odd_entry.market,
                selection=odd_entry.selection,
                bookmaker=odd_entry.bookmaker,
                odd_value=odd_entry.odd_value,
                real_probability=round(real_prob, 4),
                implied_probability=implied,
                expected_value=ev,
                classification=classification,
                confidence_level=prediction.confidence_score,
                is_highlighted=highlighted,
                reasoning=self._build_reasoning(
                    odd_entry.market, odd_entry.selection, real_prob, ev, match
                ),
            )
            recommendations.append(rec)

        return recommendations

    def _get_real_probability_for_market(
        self,
        market: str,
        selection: str,
        match: Match,
        blue_win_prob: float,
        red_win_prob: float,
        mc_results: dict,
        poisson_results: dict,
    ):
        """Mapear mercado e seleção para a probabilidade real calculada."""
        kills_mc = mc_results.get("kills", {})
        over_probs = poisson_results.get("over_probabilities", {})
        under_probs = poisson_results.get("under_probabilities", {})

        if market == "match_winner":
            if "blue" in selection.lower() or (
                match.team_blue and match.team_blue.name.lower() in selection.lower()
            ):
                return blue_win_prob
            elif "red" in selection.lower() or (
                match.team_red and match.team_red.name.lower() in selection.lower()
            ):
                return red_win_prob

        elif market in ("over_kills", "kills_total"):
            # Extrair limiar: "over_25.5" → 25.5
            import re
            match_num = re.search(r"(\d+(?:\.\d+)?)", selection)
            if match_num:
                threshold = float(match_num.group(1))
                key = f"over_{threshold}"
                return over_probs.get(key) or kills_mc.get(key)

        elif market in ("under_kills",):
            import re
            match_num = re.search(r"(\d+(?:\.\d+)?)", selection)
            if match_num:
                threshold = float(match_num.group(1))
                key = f"under_{threshold}"
                return under_probs.get(key)

        elif market == "first_blood":
            if "blue" in selection.lower():
                blue_team = match.team_blue
                return blue_team.first_blood_rate if blue_team else None
            elif "red" in selection.lower():
                red_team = match.team_red
                return red_team.first_blood_rate if red_team else None

        elif market == "first_dragon":
            if "blue" in selection.lower():
                blue_team = match.team_blue
                return blue_team.first_dragon_rate if blue_team else None
            elif "red" in selection.lower():
                red_team = match.team_red
                return red_team.first_dragon_rate if red_team else None

        return None

    def _build_reasoning(
        self,
        market: str,
        selection: str,
        real_prob: float,
        ev: float,
        match: Match,
    ) -> str:
        """Construir texto de justificativa para a recomendação."""
        blue_name = match.team_blue.name if match.team_blue else "Time Azul"
        red_name = match.team_red.name if match.team_red else "Time Vermelho"

        reasoning = (
            f"Mercado: {market} | Seleção: {selection} | "
            f"Probabilidade real: {real_prob:.1%} | EV: {ev:+.2%} | "
            f"Partida: {blue_name} vs {red_name}"
        )
        return reasoning
