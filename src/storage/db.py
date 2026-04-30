import sqlite3
import logging
import os
from src.config import DB_PATH

logger = logging.getLogger(__name__)

class FootballDB:

    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        #self.conn = sqlite3.connect(DB_PATH)
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # da mozemo da citamo po imenu kolone
        self._create_tables()

    def _create_tables(self):
        """Kreiraj tabele ako ne postoje"""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS standings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                competition TEXT,
                position INTEGER,
                team_id INTEGER,
                team_name TEXT,
                played INTEGER,
                won INTEGER,
                draw INTEGER,
                lost INTEGER,
                points INTEGER,
                goals_for INTEGER,
                goals_against INTEGER,
                goal_diff INTEGER,
                fetched_at TEXT
            );

            CREATE TABLE IF NOT EXISTS matches (
                match_id INTEGER PRIMARY KEY,
                competition TEXT,
                season TEXT,
                matchday INTEGER,
                status TEXT,
                date TEXT,
                home_team_id INTEGER,
                home_team TEXT,
                away_team_id INTEGER,
                away_team TEXT,
                home_score INTEGER,
                away_score INTEGER,
                winner TEXT,
                fetched_at TEXT
            );
        """)
        self.conn.commit()
        logger.info("Tabele OK")

    def save_standings(self, standings: list):
        """Upisuj standings u bazu"""
        if not standings:
            return

        # Obrisi stare pa upisuj nove
        competition = standings[0]["competition"]
        self.conn.execute("DELETE FROM standings WHERE competition = ?", (competition,))

        self.conn.executemany("""
            INSERT INTO standings (
                competition, position, team_id, team_name,
                played, won, draw, lost, points,
                goals_for, goals_against, goal_diff, fetched_at
            ) VALUES (
                :competition, :position, :team_id, :team_name,
                :played, :won, :draw, :lost, :points,
                :goals_for, :goals_against, :goal_diff, :fetched_at
            )
        """, standings)

        self.conn.commit()
        logger.info(f"Standings upisano: {len(standings)} timova ({competition})")

    def save_matches(self, matches: list):
        """Upisuj meceve u bazu"""
        if not matches:
            return

        self.conn.executemany("""
            INSERT OR REPLACE INTO matches (
                match_id, competition, season, matchday, status, date,
                home_team_id, home_team, away_team_id, away_team,
                home_score, away_score, winner, fetched_at
            ) VALUES (
                :match_id, :competition, :season, :matchday, :status, :date,
                :home_team_id, :home_team, :away_team_id, :away_team,
                :home_score, :away_score, :winner, :fetched_at
            )
        """, matches)

        self.conn.commit()
        logger.info(f"Mecevi upisani: {len(matches)} ({matches[0]['competition']})")

    def get_matches(self, competition: str = None, status: str = None) -> list:
        """Citaj meceve iz baze"""
        query = "SELECT * FROM matches WHERE 1=1"
        params = []

        if competition:
            query += " AND competition = ?"
            params.append(competition)
        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY date"
        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_standings(self, competition: str) -> list:
        """Citaj tabelu iz baze"""
        cursor = self.conn.execute(
            "SELECT * FROM standings WHERE competition = ? ORDER BY position",
            (competition,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def close(self):
        self.conn.close()