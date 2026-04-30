from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from src.model import FootballModel
from src.features import FeatureEngineer
from src.storage.db import FootballDB
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Football Predictor API",
    description="ML-powered football match predictions",
    version="1.0.0"
)

# CORS — da React moze da ga zove
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Ucitaj model jednom pri startu
model = FootballModel()
model._load()
db = FootballDB()

# ---- Schemas ----

class PredictionRequest(BaseModel):
    home_team_id: int
    away_team_id: int
    competition: str = "PL"

class ManualPredictionRequest(BaseModel):
    home_form: float
    away_form: float
    home_goals_avg: float
    away_goals_avg: float
    home_position: int
    away_position: int

# ---- Endpoints ----

@app.get("/")
def root():
    return {"message": "Football Predictor API radi!"}

@app.get("/standings/{competition}")
def get_standings(competition: str):
    """Tabela za ligu"""
    standings = db.get_standings(competition.upper())
    if not standings:
        raise HTTPException(status_code=404, detail="Liga nije nadjena")
    return {"competition": competition, "standings": standings}

@app.get("/matches/{competition}")
def get_matches(competition: str, status: str = None):
    """Mecevi za ligu"""
    matches = db.get_matches(
        competition=competition.upper(),
        status=status
    )
    return {"competition": competition, "matches": matches}

@app.post("/predict/manual")
def predict_manual(req: ManualPredictionRequest):
    """Predikcija sa manuelnim feature-ima"""
    try:
        result = model.predict(
            home_form=req.home_form,
            away_form=req.away_form,
            home_goals_avg=req.home_goals_avg,
            away_goals_avg=req.away_goals_avg,
            home_position=req.home_position,
            away_position=req.away_position
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/match")
def predict_match(req: PredictionRequest):
    """Predikcija na osnovu team ID-eva iz baze"""
    try:
        fe = FeatureEngineer()
        all_matches = db.get_matches(competition=req.competition)
        standings = db.get_standings(req.competition)

        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()

        home_form = fe._get_team_form(all_matches, req.home_team_id, now)
        away_form = fe._get_team_form(all_matches, req.away_team_id, now)
        home_goals = fe._get_goals_avg(all_matches, req.home_team_id, now)
        away_goals = fe._get_goals_avg(all_matches, req.away_team_id, now)
        home_pos = fe._get_position(standings, req.home_team_id)
        away_pos = fe._get_position(standings, req.away_team_id)

        result = model.predict(
            home_form=home_form,
            away_form=away_form,
            home_goals_avg=home_goals,
            away_goals_avg=away_goals,
            home_position=home_pos,
            away_position=away_pos
        )

        # Info o timovima
        home_name = next((m["home_team"] for m in all_matches if m["home_team_id"] == req.home_team_id), "Unknown")
        away_name = next((m["away_team"] for m in all_matches if m["away_team_id"] == req.away_team_id), "Unknown")

        return {
            "home_team": home_name,
            "away_team": away_name,
            "prediction": result,
            "features": {
                "home_form": home_form,
                "away_form": away_form,
                "home_goals_avg": home_goals,
                "away_goals_avg": away_goals,
                "home_position": home_pos,
                "away_position": away_pos
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))