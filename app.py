# app.py — Servidor webhook para copiar trades a MT5
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "mi_token_secreto_123")
MT5_EA_URL = os.environ.get("MT5_EA_URL", "http://localhost:8080/trade")

CONVERSION = {
    "MNQ": {"symbol": "NAS100", "lot_per_contract": 0.1},
    "MES": {"symbol": "SP500",  "lot_per_contract": 0.1},
    "MYM": {"symbol": "US30",   "lot_per_contract": 0.1},
}

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data.get("token") != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    instrumento = data.get("instrument", "MNQ").upper()
    accion      = data.get("action", "buy").lower()
    contratos   = float(data.get("contracts", 1))
    sl_price    = data.get("sl", 0)
    tp_price    = data.get("tp", 0)

    if instrumento not in CONVERSION:
        return jsonify({"error": "Instrumento no soportado"}), 400

    config = CONVERSION[instrumento]
    lotes  = round(contratos * config["lot_per_contract"], 2)
    symbol = config["symbol"]

    payload = {
        "symbol":  symbol,
        "action":  accion,
        "lots":    lotes,
        "sl":      sl_price,
        "tp":      tp_price,
    }

    try:
        r = requests.post(MT5_EA_URL, json=payload, timeout=5)
        return jsonify({"status": "ok", "lotes": lotes, "symbol": symbol})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def health():
    return "Servidor activo"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)