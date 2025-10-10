from flask import Flask, request, jsonify
import pickle
import pandas as pd

app = Flask(__name__)

# ========================
# CARICAMENTO MODELLO
# ========================
with open("fitness_model.pkl", "rb") as f:
    model = pickle.load(f)

# ========================
# ENDPOINT PREDIZIONE
# ========================
@app.route("/api/predict", methods=["POST"])
def predict_fitness():
    try:
        data = request.json
        # Controllo campi richiesti
        required_fields = ['durata_media', 'numero_allenamenti', 'peso_medio', 'bmi_medio', 'massa_grassa_media']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo mancante: {field}"}), 400

        # Creazione DataFrame singolo per predizione
        df = pd.DataFrame([data])

        # Predizione
        prediction = model.predict(df)[0]

        return jsonify({"livello_fitness": prediction})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========================
# AVVIO SERVER
# ========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
