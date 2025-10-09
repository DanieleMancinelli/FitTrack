from flask import Flask, request, jsonify, session
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Permetti richieste cross-origin con sessione
CORS(app, supports_credentials=True)

# Configurazione del database
db_config = {
    'host': 'mysql-54fee60-correzione-verifica21-10.j.aivencloud.com',
    'user': 'avnadmin',
    'password': 'AVNS_iY9T-ZLq2IPFDEue9p6',
    'database': 'W3Schools',
    'port': 19384
}

# ========================
# FUNZIONI DB
# ========================
def get_connection():
    return mysql.connector.connect(**db_config)

def fetch_all(query, params=None):
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params or ())
        rows = cur.fetchall()
        return rows
    except Error as e:
        print("DB Error:", e)
        return []
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()

def fetch_one(query, params=None):
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params or ())
        row = cur.fetchone()
        return row
    except Error as e:
        print("DB Error:", e)
        return None
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()

def execute(query, params=None):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params or ())
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print("DB Error:", e)
        return None
    finally:
        if conn.is_connected():
            cur.close()
            conn.close()


# ========================
# ENDPOINT API
# ========================

# --- LOGIN ---
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email e password richieste"}), 400

    user = fetch_one("SELECT * FROM Utente WHERE email=%s AND password_hash=%s", (email, password))
    if not user:
        return jsonify({"error": "Credenziali non valide"}), 401

    # salva la sessione
    session["user_id"] = user["id_utente"]
    session["ruolo"] = user["ruolo"]
    session["nome"] = user["nome"]

    return jsonify({"message": "Login effettuato", "user": {"id": user["id_utente"], "nome": user["nome"], "ruolo": user["ruolo"]}})


# --- LOGOUT ---
@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"message": "Logout effettuato"})


# --- ALLENAMENTI (GET) ---
@app.route("/api/allenamenti", methods=["GET"])
def get_allenamenti():
    if "user_id" not in session:
        return jsonify({"error": "Non autorizzato"}), 401

    user_id = session["user_id"]
    ruolo = session["ruolo"]

    if ruolo == "admin":
        allenamenti = fetch_all("SELECT * FROM Allenamento ORDER BY data DESC")
    else:
        allenamenti = fetch_all("SELECT * FROM Allenamento WHERE id_utente=%s ORDER BY data DESC", (user_id,))

    return jsonify(allenamenti)


# --- ALLENAMENTI (POST) ---
@app.route("/api/allenamenti", methods=["POST"])
def add_allenamento():
    if "user_id" not in session:
        return jsonify({"error": "Non autorizzato"}), 401

    data = request.get_json() or {}
    data_all = data.get("data")
    durata = data.get("durata")
    note = data.get("note", "")

    if not data_all or not durata:
        return jsonify({"error": "Campi obbligatori: data, durata"}), 400

    last_id = execute(
        "INSERT INTO Allenamento (data, durata, note, id_utente) VALUES (%s, %s, %s, %s)",
        (data_all, durata, note, session["user_id"])
    )

    if last_id:
        return jsonify({"message": "Allenamento aggiunto", "id_allenamento": last_id}), 201
    else:
        return jsonify({"error": "Errore nel salvataggio"}), 500


# --- PROGRESSI (GET) ---
@app.route("/api/progressi", methods=["GET"])
def get_progressi():
    if "user_id" not in session:
        return jsonify({"error": "Non autorizzato"}), 401

    user_id = session["user_id"]
    ruolo = session["ruolo"]

    if ruolo == "admin":
        progressi = fetch_all("SELECT * FROM Progresso ORDER BY data DESC")
    else:
        progressi = fetch_all("SELECT * FROM Progresso WHERE id_utente=%s ORDER BY data DESC", (user_id,))

    return jsonify(progressi)


# --- PROGRESSI (POST) ---
@app.route("/api/progressi", methods=["POST"])
def add_progresso():
    if "user_id" not in session:
        return jsonify({"error": "Non autorizzato"}), 401

    data = request.get_json() or {}
    data_prog = data.get("data")
    peso = data.get("peso")
    altezza = data.get("altezza")
    bmi = data.get("bmi")
    massa_grassa = data.get("massa_grassa")
    note = data.get("note", "")

    if not data_prog or not peso or not altezza:
        return jsonify({"error": "Campi obbligatori: data, peso, altezza"}), 400

    last_id = execute(
        "INSERT INTO Progresso (id_utente, data, peso, altezza, bmi, massa_grassa, note) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (session["user_id"], data_prog, peso, altezza, bmi, massa_grassa, note)
    )

    if last_id:
        return jsonify({"message": "Progresso aggiunto", "id_progresso": last_id}), 201
    else:
        return jsonify({"error": "Errore nel salvataggio"}), 500


# --- HEALTH CHECK ---
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)
