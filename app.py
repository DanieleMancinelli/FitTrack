from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Connessione MySQL
db = mysql.connector.connect(
    host="mysql-54fee60-correzione-verifica21-10.j.aivencloud.com",
    user="avnadmin",
    password="AVNS_iY9T-ZLq2IPFDEue9p6",   # la tua password MySQL
    database="defaultdb"
    port=19384
)
cursor = db.cursor(dictionary=True)

# ========================
# HOME / DASHBOARD
# ========================
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    cursor.execute("SELECT * FROM Allenamento WHERE id_utente=%s ORDER BY data DESC", (user_id,))
    allenamenti = cursor.fetchall()
    
    cursor.execute("SELECT * FROM Progresso WHERE id_utente=%s ORDER BY data DESC", (user_id,))
    progressi = cursor.fetchall()
    
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
        password = request.form['password']  # in chiaro
        
        cursor.execute("SELECT * FROM Utente WHERE email=%s", (email,))
        account = cursor.fetchone()
        if account:
            flash("Email già registrata", "danger")
            return redirect(url_for('register'))
        
        cursor.execute(
            "INSERT INTO Utente (nome, cognome, email, password_hash) VALUES (%s,%s,%s,%s)",
            (nome, cognome, email, password)
        )
        db.commit()
        flash("Registrazione avvenuta con successo", "success")
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
        
        cursor.execute("SELECT * FROM Utente WHERE email=%s AND password_hash=%s", (email, password))
        user = cursor.fetchone()
        
        if user:
            session['user_id'] = user['id_utente']
            session['user_nome'] = user['nome']
            return redirect(url_for('dashboard'))
        else:
            flash("Email o password errati", "danger")
            return redirect(url_for('login'))
    
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
