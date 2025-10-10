from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Configurazione database
db_config = {
    'host': 'mysql-54fee60-correzione-verifica21-10.j.aivencloud.com',
    'user': 'avnadmin',
    'password': 'AVNS_iY9T-ZLq2IPFDEue9p6',
    'database': 'FitTrack',
    'port': 19384
}

# ========================
# FUNZIONI UTILI
# ========================
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
        if session.get('ruolo') == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# ========================
# DASHBOARD UTENTE
# ========================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    allenamenti = get_table_data("SELECT * FROM Allenamento WHERE id_utente=%s ORDER BY data DESC", (user_id,))
    progressi = get_table_data("SELECT * FROM Progresso WHERE id_utente=%s ORDER BY data DESC", (user_id,))

    return render_template('dashboard.html', nome=session.get('user_nome'), allenamenti=allenamenti, progressi=progressi)

# ========================
# DASHBOARD ADMIN
# ========================
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('ruolo') != 'admin':
        return redirect(url_for('login'))

    utenti = get_table_data("SELECT id_utente, nome, cognome, email, ruolo FROM Utente")
    return render_template('dashboard_admin.html', utenti=utenti)

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

        # controlla se esiste già
        account = get_table_data("SELECT * FROM Utente WHERE email=%s", (email,))
        if account:
            return render_template('register.html', errore="Email già registrata!")

        hashed_pw = generate_password_hash(password)
        execute_query(
            "INSERT INTO Utente (nome, cognome, email, password_hash, ruolo, data_iscrizione) VALUES (%s,%s,%s,%s,%s,CURDATE())",
            (nome, cognome, email, hashed_pw, 'utente')
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

        user = get_table_data("SELECT * FROM Utente WHERE email=%s", (email,))
        if user and check_password_hash(user[0]['password_hash'], password):
            session['user_id'] = user[0]['id_utente']
            session['user_nome'] = user[0]['nome']
            session['ruolo'] = user[0]['ruolo']
            if user[0]['ruolo'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', errore="Credenziali errate!")

    return render_template('login.html')

# ========================
# LOGOUT
# ========================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ========================
# AVVIO SERVER
# ========================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
