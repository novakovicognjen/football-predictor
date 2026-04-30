#Ovo je wrapper

#umesto da svuda pisem
#requests.get("https://api.football-data.org/v4/matches", headers={"X-Auth-Token": "..."})
#client.get_matches("PL")
#client.get_standings("BL1")
import requests
import time
import logging
from src.config import API_KEY, BASE_URL

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

class FootballApiClient:

    def __init__(self):
        self.session=requests.Session() #pamti stanje
        self.session.headers.update({"X-Auth-Token" : API_KEY})
        self.base_url = BASE_URL
   
    def _get(self,endpoint : str, params : dict=None) -> dict:
        """Bazni GET poziv - koriste sve metode ispod"""
        url=f"{self.base_url}/{endpoint}"
        try:
            response = self.session.get(url,params=params)
            if response.status_code==429: #Rate limit
                logger.warning("Rate limit hit, cekam 60s...")
                time.sleep(60)
                response=self.session.get(url,params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API greska: {e}")
            return {}
    
    def get_competitions(self) -> dict:
        """Sve dostupne lige"""
        return self._get("competitions")
    def get_matches(self,competition_code: str, season: int=None) ->dict:
        """Svi mecevi za ligu"""
        params = {}
        if season:
            params["season"]=season
        return self._get(f"competitions/{competition_code}/matches",params=params)
    
    def get_standings(self,competition_code: str, season: int=None)-> dict:
        """Tabela za ligu"""
        params={}
        if season:
            params["season"]=season
        return self._get(f"competitions/{competition_code}/standings",params=params)
    
    def get_team_matches(self,team_id:int,limit:int=10)->dict:
        """Zadnjih N meceva tima - za formu"""
        params = {"limit":limit}
        return self._get(f"teams/{team_id}/matches",params=params)
    