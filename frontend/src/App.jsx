import { useState, useEffect } from "react"
import axios from "axios"

const API = "http://localhost:8000"

export default function App() {
  const [standings, setStandings] = useState([])
  const [prediction, setPrediction] = useState(null)
  const [homeId, setHomeId] = useState("")
  const [awayId, setAwayId] = useState("")
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    axios.get(`${API}/standings/PL`)
      .then(res => setStandings(res.data.standings))
  }, [])

  const predict = async () => {
    setLoading(true)
    try {
      const res = await axios.post(`${API}/predict/match`, {
        home_team_id: parseInt(homeId),
        away_team_id: parseInt(awayId),
        competition: "PL"
      })
      setPrediction(res.data)
    } catch (e) {
      alert("Error! Check team IDs")
    }
    setLoading(false)
  }

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: 24 }}>

      {/* Header */}
      <div style={{ textAlign: "center", marginBottom: 32 }}>
        <h1 style={{ fontSize: 32, fontWeight: "bold", color: "#38bdf8" }}>
          ⚽ Football Predictor
        </h1>
        <p style={{ color: "#94a3b8", marginTop: 8 }}>
          ML-powered match predictions
        </p>
      </div>

      {/* Predikcija */}
      <div style={{
        background: "#1e293b", borderRadius: 12,
        padding: 24, marginBottom: 32
      }}>
        <h2 style={{ fontSize: 20, marginBottom: 16, color: "#38bdf8" }}>
          Predict Match
        </h2>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          <input
            placeholder="Home Team ID (e.g. 57)"
            value={homeId}
            onChange={e => setHomeId(e.target.value)}
            style={{
              padding: "10px 16px", borderRadius: 8,
              border: "1px solid #334155", background: "#0f172a",
              color: "white", fontSize: 14, flex: 1
            }}
          />
          <input
            placeholder="Away Team ID (e.g. 65)"
            value={awayId}
            onChange={e => setAwayId(e.target.value)}
            style={{
              padding: "10px 16px", borderRadius: 8,
              border: "1px solid #334155", background: "#0f172a",
              color: "white", fontSize: 14, flex: 1
            }}
          />
          <button
            onClick={predict}
            disabled={loading}
            style={{
              padding: "10px 24px", borderRadius: 8,
              background: "#38bdf8", color: "#0f172a",
              fontWeight: "bold", border: "none",
              cursor: "pointer", fontSize: 14
            }}
          >
            {loading ? "..." : "Predict"}
          </button>
        </div>

        {/* Rezultat predikcije */}
        {prediction && (
          <div style={{ marginTop: 24 }}>
            <h3 style={{ marginBottom: 12, color: "#94a3b8" }}>
              {prediction.home_team} vs {prediction.away_team}
            </h3>
            <div style={{ display: "flex", gap: 12 }}>
              {[
                { label: "Home Win", value: prediction.prediction.home_win, key: "H" },
                { label: "Draw", value: prediction.prediction.draw, key: "D" },
                { label: "Away Win", value: prediction.prediction.away_win, key: "A" }
              ].map(item => (
                <div key={item.key} style={{
                  flex: 1, background: prediction.prediction.prediction === item.key
                    ? "#0369a1" : "#0f172a",
                  borderRadius: 8, padding: 16, textAlign: "center",
                  border: prediction.prediction.prediction === item.key
                    ? "2px solid #38bdf8" : "1px solid #334155"
                }}>
                  <div style={{ fontSize: 24, fontWeight: "bold", color: "#38bdf8" }}>
                    {(item.value * 100).toFixed(1)}%
                  </div>
                  <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 4 }}>
                    {item.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Standings tabela */}
      <div style={{ background: "#1e293b", borderRadius: 12, padding: 24 }}>
        <h2 style={{ fontSize: 20, marginBottom: 16, color: "#38bdf8" }}>
          Premier League Standings
        </h2>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ color: "#94a3b8", fontSize: 12, textAlign: "left" }}>
              <th style={{ padding: "8px 12px" }}>#</th>
              <th style={{ padding: "8px 12px" }}>Team</th>
              <th style={{ padding: "8px 12px" }}>Played</th>
              <th style={{ padding: "8px 12px" }}>Won</th>
              <th style={{ padding: "8px 12px" }}>Draw</th>
              <th style={{ padding: "8px 12px" }}>Lost</th>
              <th style={{ padding: "8px 12px" }}>Points</th>
              <th style={{ padding: "8px 12px" }}>ID</th>
            </tr>
          </thead>
          <tbody>
            {standings.map((team, i) => (
              <tr key={team.team_id} style={{
                borderTop: "1px solid #334155",
                background: i % 2 === 0 ? "#0f172a22" : "transparent"
              }}>
                <td style={{ padding: "10px 12px", color: "#94a3b8" }}>{team.position}</td>
                <td style={{ padding: "10px 12px", fontWeight: "500" }}>{team.team_name}</td>
                <td style={{ padding: "10px 12px", color: "#94a3b8" }}>{team.played}</td>
                <td style={{ padding: "10px 12px", color: "#4ade80" }}>{team.won}</td>
                <td style={{ padding: "10px 12px", color: "#facc15" }}>{team.draw}</td>
                <td style={{ padding: "10px 12px", color: "#f87171" }}>{team.lost}</td>
                <td style={{ padding: "10px 12px", fontWeight: "bold", color: "#38bdf8" }}>{team.points}</td>
                <td style={{ padding: "10px 12px", color: "#475569", fontSize: 12 }}>{team.team_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  )
}