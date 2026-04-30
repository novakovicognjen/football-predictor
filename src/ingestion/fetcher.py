import json
import os
import logging
from datetime import datetime
from src.ingestion.api_client import FootballApiClient
from src.config import COMPETITIONS, CURRENT_SEASON, DATA_RAW_DIR

logger = logging.getLogger(__name__)

class FootballFetcher:

    def __init__(self):
        self.client = FootballApiClient()
    def _save_raw(self,data:dict,filename:str):
        """Sacuvaj sirovi JSON u data/raw/"""
        os.makedirs(DATA_RAW_DIR,exist_ok=True)
        filepath=os.path.join(DATA_RAW_DIR,filename)
        with open(filepath,"w",encoding="utf-8") as f:
            json.dump(data,f,indent=2,ensure_ascii=False)
        logger.info(f"Sacuvano :{filepath}")
    
    def fetch_standings(self,competition_code:str)->list:
        """Dohvati i sacuvaj tabelu za ligu"""
        logger.info(f"Fetchujem standings za {competition_code}...")
        data=self.client.get_standings(competition_code)

        if not data:
            logger.warning(f"Nema podataka za {competition_code}")
            return []
        #sacuvaj sirovi JSON
        filename= f"standings_{competition_code}_{datetime.now().strftime('%Y%m%d')}.json"
        self._save_raw(data,filename)
        #Izvuci samo tabelu
        standings=[]
        for standing in data.get("standings",[]):
            if standing["type"]=="TOTAL":
                for row in standing["table"]:
                    standings.append({
                        "competition":competition_code,
                        "position":row["position"],
                        "team_id":row["team"]["id"],
                        "team_name": row["team"]["name"],
                        "played":row["playedGames"],
                        "won":row["won"],
                        "draw":row["draw"],
                        "lost":row["lost"],
                        "points":row["points"],
                        "goals_for":row["goalsFor"],
                        "goals_against":row["goalsAgainst"],
                        "goal_diff":row["goalDifference"],
                        "fetched_at":datetime.now().isoformat()
                    })
        logger.info(f" -> {len(standings)} timova")
        return standings
    def fetch_matches(self,competition_code:str)->list:
        """Dohvati i sacuvaj meceve za ligu"""
        logger.info(f"Fetchujem meceve za {competition_code}...")
        data=self.client.get_matches(competition_code)

        if not data:
            logger.warning(f"Nema meceva za {competition_code}")
            return []

        filename = f"matches_{competition_code}_{datetime.now().strftime('%Y%m%d')}.json"
        self._save_raw(data,filename)
        
        matches=[]
        for m in data.get("matches",[]):
            matches.append({
                "match_id": m["id"],
                "competition": competition_code,
                "season": m["season"]["startDate"][:4],
                "matchday": m.get("matchday"),
                "status": m["status"],
                "date": m["utcDate"],
                "home_team_id": m["homeTeam"]["id"],
                "home_team": m["homeTeam"]["name"],
                "away_team_id": m["awayTeam"]["id"],
                "away_team": m["awayTeam"]["name"],
                "home_score": m["score"]["fullTime"].get("home"),
                "away_score": m["score"]["fullTime"].get("away"),
                "winner": m["score"].get("winner"),
                "fetched_at": datetime.now().isoformat()
            })

        finished=[x for x in matches if x["status"]=="FINISHED"]
        logger.info(f" -> {len(matches)} ukupno, {len(finished)} zavrsenih")
        return matches
    def fetch_all(self)-> dict:
        """Dohvati sve podatke za sve lige"""
        results={}
        for code in COMPETITIONS:
            results[code]={
                "standings":self.fetch_standings(code),
                "matches":self.fetch_matches(code)
            }
        return results