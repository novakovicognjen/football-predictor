import pandas as pd
import logging
from src.storage.db import FootballDB

logger = logging.getLogger(__name__)

class FeatureEngineer:

    def __init__(self):
        self.db = FootballDB()

    def _get_team_form(self, matches: list, team_id: int, before_date: str, n: int = 5) -> float:
        """Forma tima — % pobeda u zadnjih N mečeva"""
        team_matches = [
            m for m in matches
            if (m["home_team_id"] == team_id or m["away_team_id"] == team_id)
            and m["status"] == "FINISHED"
            and m["date"] < before_date
        ]
        team_matches = sorted(team_matches, key=lambda x: x["date"], reverse=True)[:n]

        if not team_matches:
            return 0.5  # neutral ako nema podataka

        wins = 0
        for m in team_matches:
            if m["home_team_id"] == team_id and m["winner"] == "HOME_TEAM":
                wins += 1
            elif m["away_team_id"] == team_id and m["winner"] == "AWAY_TEAM":
                wins += 1

        return wins / len(team_matches)

    def _get_goals_avg(self, matches: list, team_id: int, before_date: str, n: int = 5) -> float:
        """Prosek golova tima u zadnjih N mečeva"""
        team_matches = [
            m for m in matches
            if (m["home_team_id"] == team_id or m["away_team_id"] == team_id)
            and m["status"] == "FINISHED"
            and m["date"] < before_date
        ]
        team_matches = sorted(team_matches, key=lambda x: x["date"], reverse=True)[:n]

        if not team_matches:
            return 1.0

        total_goals = 0
        for m in team_matches:
            if m["home_team_id"] == team_id:
                total_goals += m["home_score"] or 0
            else:
                total_goals += m["away_score"] or 0

        return total_goals / len(team_matches)

    def _get_position(self, standings: list, team_id: int) -> int:
        """Pozicija na tabeli"""
        for row in standings:
            if row["team_id"] == team_id:
                return row["position"]
        return 10  # neutral ako nema

    def _get_result(self, match: dict) -> str:
        """Rezultat za ML: H, D, A"""
        if match["winner"] == "HOME_TEAM":
            return "H"
        elif match["winner"] == "AWAY_TEAM":
            return "A"
        else:
            return "D"

    def build_features(self, competition: str = "PL") -> pd.DataFrame:
        """Napravi feature tabelu za sve zavrsene meceve"""
        all_matches = self.db.get_matches(competition=competition)
        standings = self.db.get_standings(competition)
        finished = [m for m in all_matches if m["status"] == "FINISHED"]

        logger.info(f"Gradim features za {len(finished)} meceva...")

        rows = []
        for match in finished:
            home_id = match["home_team_id"]
            away_id = match["away_team_id"]
            date = match["date"]

            row = {
                "match_id":       match["match_id"],
                "date":           date,
                "home_team":      match["home_team"],
                "away_team":      match["away_team"],
                "home_form":      self._get_team_form(all_matches, home_id, date),
                "away_form":      self._get_team_form(all_matches, away_id, date),
                "home_goals_avg": self._get_goals_avg(all_matches, home_id, date),
                "away_goals_avg": self._get_goals_avg(all_matches, away_id, date),
                "home_position":  self._get_position(standings, home_id),
                "away_position":  self._get_position(standings, away_id),
                "result":         self._get_result(match)
            }
            rows.append(row)

        df = pd.DataFrame(rows)
        logger.info(f"Feature tabela: {df.shape[0]} redova, {df.shape[1]} kolona")
        return df