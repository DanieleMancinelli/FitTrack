from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd

app = Flask(__name__)

# ========================
# CARICAMENTO MODELLO
# ========================
with open("fitness_model.pkl", "rb") as f:
    model = pickle.load(f)

# ========================
# PAGINA WEB
# ========================
@app.route("/")
def home():
    return render_template("predizione.html")

# ========================
# ENDPOINT DI PREDIZIONE
# ========================
@app.route("/predict", methods=["POST"])
def predict_fitness():
    try:
        data = request.get_json() if request.is_json else request.form

        durata_media = float(data.get("durata_media"))
        numero_allenamenti = float(data.get("numero_allenamenti"))
        peso_medio = float(data.get("peso_medio"))
        bmi_medio = float(data.get("bmi_medio"))
        massa_grassa_media = float(data.get("massa_grassa_media"))

        df = pd.DataFrame([{
            "durata_media": durata_media,
            "numero_allenamenti": numero_allenamenti,
            "peso_medio": peso_medio,
            "bmi_medio": bmi_medio,
            "massa_grassa_media": massa_grassa_media
        }])

        prediction = model.predict(df)[0]
        return jsonify({"livello_fitness": prediction})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
