import pandas as pd
import numpy as np
import pickle
import os
import logging
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from src.features import FeatureEngineer
from src.config import MODELS_DIR

logger = logging.getLogger(__name__)

FEATURE_COLS = [
    "home_form",
    "away_form", 
    "home_goals_avg",
    "away_goals_avg",
    "home_position",
    "away_position"
]

class FootballModel:

    def __init__(self):
        self.model = None
        self.encoder = LabelEncoder()
        self.model_path = os.path.join(MODELS_DIR, "football_model.pkl")
        self.encoder_path = os.path.join(MODELS_DIR, "label_encoder.pkl")

    def train(self, competitions: list = ["PL"]):
        """Treniraj model na istorijskim mecevima"""
        fe = FeatureEngineer()

        # Spoji sve lige u jedan DataFrame
        all_dfs = []
        for comp in competitions:
            df = fe.build_features(comp)
            if len(df) > 0:
                all_dfs.append(df)
                logger.info(f"{comp}: {len(df)} meceva")

        df = pd.concat(all_dfs, ignore_index=True)
        logger.info(f"Ukupno: {len(df)} meceva iz {len(competitions)} liga...")

        # Pripremi X i y
        X = df[FEATURE_COLS]
        y = self.encoder.fit_transform(df["result"])

        # Train/test split — 80/20
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")

        # XGBoost model
        self.model = XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            objective="multi:softprob",
            num_class=3,
            random_state=42,
            eval_metric="mlogloss"
        )

        self.model.fit(X_train, y_train)

        # Evaluacija
        y_pred = self.model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        logger.info(f"Accuracy: {acc:.2%}")
        print(f"\nAccuracy: {acc:.2%}")
        print("\nClassification Report:")
        print(classification_report(
            y_test, y_pred,
            target_names=self.encoder.classes_
        ))

        # Sacuvaj model
        self._save()
        return acc

    def predict(self, home_form, away_form, home_goals_avg,
                away_goals_avg, home_position, away_position) -> dict:
        """Predvidi ishod meca"""
        if self.model is None:
            self._load()

        X = pd.DataFrame([{
            "home_form":      home_form,
            "away_form":      away_form,
            "home_goals_avg": home_goals_avg,
            "away_goals_avg": away_goals_avg,
            "home_position":  home_position,
            "away_position":  away_position
        }])

        proba = self.model.predict_proba(X)[0]

        # Mapiranje klasa
        classes = self.encoder.classes_  # ['A', 'D', 'H']
        result = {cls: round(float(p), 3) for cls, p in zip(classes, proba)}

        return {
            "home_win":  result.get("H", 0),
            "draw":      result.get("D", 0),
            "away_win":  result.get("A", 0),
            "prediction": max(result, key=result.get)
        }

    def _save(self):
        """Sacuvaj model na disk"""
        os.makedirs(MODELS_DIR, exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump(self.model, f)
        with open(self.encoder_path, "wb") as f:
            pickle.dump(self.encoder, f)
        logger.info(f"Model sacuvan: {self.model_path}")

    def _load(self):
        """Ucitaj model sa diska"""
        with open(self.model_path, "rb") as f:
            self.model = pickle.load(f)
        with open(self.encoder_path, "rb") as f:
            self.encoder = pickle.load(f)
        logger.info("Model ucitan")