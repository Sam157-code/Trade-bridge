# app.py — Servidor webhook para copiar trades a MT5 (v2)
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "mi_token_secreto_123")

CONVERSION = {
    "MNQ": {"symbol": "NAS100", "lot_per_contract": 0.1},
    "MES": {"symbol": "SP500",  "lot_per_contract": 0.1},
    "MYM": {"symbol": "US30",   "lot_per_contract": 0.1},
}

pending_signal = {}

@app.route("/webhook", methods=["POST"])
def webhook():
    global pending_signal
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

    pending_signal = {
        "symbol": config["symbol"],
        "action": accion,
        "lots":   lotes,
        "sl":     sl_price,
        "tp":     tp_price,
    }

    return jsonify({"status": "ok", "lotes": lotes})

@app.route("/signal", methods=["POST"])
def signal():
    global pending_signal
    data = request.get_json()

    if data.get("token") != SECRET_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    if not pending_signal:
        return jsonify({"status": "no_signal"})

    signal_to_send = pending_signal.copy()
    pending_signal = {}
    return jsonify(signal_to_send)

@app.route("/")
def health():
    return "Servidor activo v2"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
