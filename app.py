from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configurazione database (metti i tuoi dati qui)
db_config = {
    'host': 'mysql-54fee60-correzione-verifica21-10.j.aivencloud.com',
    'user': 'avnadmin',
    'password': 'AVNS_iY9T-ZLq2IPFDEue9p6',
    'database': 'FitTrack',
    'port': 19384
}

# Funzione per eseguire query SELECT
def get_table_data(query, params=None):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        return rows
    except Error as e:
        print(f"Errore SELECT: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Funzione per eseguire query INSERT/UPDATE/DELETE
def execute_query(query, params=None):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        connection.commit()
    except Error as e:
        print(f"Errore INSERT/UPDATE: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# ========================
# HOME
# ========================
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# ========================
# DASHBOARD
# ========================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    allenamenti = get_table_data("SELECT * FROM Allenamento WHERE id_utente=%s ORDER BY data DESC", (user_id,))
    progressi = get_table_data("SELECT * FROM Progresso WHERE id_utente=%s ORDER BY data DESC", (user_id,))

    return render_template('dashboard.html', allenamenti=allenamenti, progressi=progressi)

# ========================
# REGISTRAZIONE
# ========================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        cognome = request.form['cognome']
        email = request.form['email']
        password = request.form['password']

        # Controllo se esiste già
        account = get_table_data("SELECT * FROM Utente WHERE email=%s", (email,))
        if account:
            return "Email già registrata!"

        execute_query(
            "INSERT INTO Utente (nome, cognome, email, password_hash, data_iscrizione) VALUES (%s,%s,%s,%s,CURDATE())",
            (nome, cognome, email, password)
        )
        return redirect(url_for('login'))

    return render_template('register.html')

# ========================
# LOGIN
# ========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = get_table_data("SELECT * FROM Utente WHERE email=%s AND password_hash=%s", (email, password))
        if user:
            session['user_id'] = user[0]['id_utente']
            session['user_nome'] = user[0]['nome']
            return redirect(url_for('dashboard'))
        else:
            return "Credenziali errate!"

    return render_template('login.html')

# ========================
# LOGOUT
# ========================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ========================
# RUN SERVER
# ========================
if __name__ == '__main__':
    app.run(debug=True)
