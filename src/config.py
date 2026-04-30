from dotenv import load_dotenv
import os

load_dotenv()

API_KEY=os.getenv("FOOTBALL_API_KEY")
BASE_URL=os.getenv("BASE_URL","https://api.football-data.org/v4")

COMPETITIONS={
        "PL":  "Premier League",
    "PD":  "La Liga",
    "BL1": "Bundesliga",
    "WC":  "FIFA World Cup",
    "CL":  "Champions League",
}

CURRENT_SEASON=2024


BASE_DIR=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR=os.path.join(BASE_DIR,"data","raw")
DATA_PROCESSED_DIR=os.path.join(BASE_DIR,"data","raw")
DB_PATH=os.path.join(BASE_DIR,"data","football.db")
MODELS_DIR=os.path.join(BASE_DIR,"models")