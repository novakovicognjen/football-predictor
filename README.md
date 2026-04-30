# Football Predictor

Full-stack application for football match prediction using machine learning.

---

## Overview

This project is an end-to-end system that:

- Fetches football data from an external API  
- Processes and prepares data  
- Applies a machine learning model for predictions  
- Exposes a REST API using FastAPI  
- Provides a frontend UI for interaction  

---

## Architecture

Frontend (React)  
↓  
FastAPI Backend  
↓  
Data Processing & Feature Engineering  
↓  
Machine Learning Model (XGBoost)  
↓  
Prediction Response  

---

## Tech Stack

- Python (FastAPI, Pandas, NumPy)  
- XGBoost  
- React (Vite)  
- REST API  

---

## Data Source

https://www.football-data.org/

---

## How to Run

### Backend

pip install fastapi uvicorn pandas numpy xgboost pydantic python-dotenv  
uvicorn src.api.main:app --reload  

API docs:  
http://127.0.0.1:8000/docs  

---

### Frontend

cd frontend  
npm install  
npm run dev  

http://localhost:5173  

---

## Environment Variables

Create a `.env` file:

FOOTBALL_API_KEY=your_api_key_here  

---

## Features

- Match prediction (home win / draw / away win)  
- League standings visualization  
- REST API endpoints  
- Interactive frontend  

---

## Future Improvements

- Add player-level features (injuries, lineups)  
- Improve model accuracy  
- Include in-game events such as injuries, red cards, and ball possesion.

---

## Notes

This project is a work in progress focused on building an end-to-end data pipeline and ML system.

---

## Author

Ognjen Novaković