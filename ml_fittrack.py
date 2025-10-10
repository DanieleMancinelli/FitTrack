import mysql.connector
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import pickle

# ========================
# CONFIGURAZIONE DATABASE
# ========================
db_config = {
    'host': 'mysql-54fee60-correzione-verifica21-10.j.aivencloud.com',
    'user': 'avnadmin',
    'password': 'AVNS_iY9T-ZLq2IPFDEue9p6',
    'database': 'FitTrack',   # 👈 nome del tuo vero database
    'port': 19384
}

# ========================
# CONNESSIONE E QUERY
# ========================
try:
    conn = mysql.connector.connect(**db_config)
    print("✅ Connessione al database riuscita")

    query = """
        SELECT 
            u.id_utente,
            u.nome,
            u.cognome,
            AVG(a.durata) AS durata_media,
            COUNT(a.id_allenamento) AS numero_allenamenti,
            AVG(p.peso) AS peso_medio,
            AVG(p.bmi) AS bmi_medio,
            AVG(p.massa_grassa) AS massa_grassa_media
        FROM Utente u
        LEFT JOIN Allenamento a ON u.id_utente = a.id_utente
        LEFT JOIN Progresso p ON u.id_utente = p.id_utente
        GROUP BY u.id_utente;
    """

    df = pd.read_sql(query, conn)
    conn.close()

except Exception as e:
    print("❌ Errore durante la connessione o query:", e)
    exit()

# ========================
# ANALISI E PREPARAZIONE
# ========================
print("\n📊 Dati estratti dal database:")
print(df.head())

# Sostituisco eventuali valori null con 0
df = df.fillna(0)

# ========================
# CREAZIONE LIVELLO FITNESS REALE
# ========================
def classifica_fitness(row):
    # logica semplice e coerente basata sui dati reali
    if row['durata_media'] == 0 or row['bmi_medio'] == 0:
        return 'scarso'
    elif row['bmi_medio'] < 20 and row['durata_media'] > 40:
        return 'eccellente'
    elif row['bmi_medio'] < 25 and row['durata_media'] > 30:
        return 'buono'
    elif row['bmi_medio'] < 30 and row['durata_media'] > 20:
        return 'medio'
    else:
        return 'scarso'

df['livello_fitness'] = df.apply(classifica_fitness, axis=1)

print("\n📈 Livelli di fitness generati automaticamente:")
print(df[['nome', 'cognome', 'livello_fitness']])

# ========================
# ADDDESTRAMENTO MODELLO
# ========================
X = df[['durata_media', 'numero_allenamenti', 'peso_medio', 'bmi_medio', 'massa_grassa_media']]
y = df['livello_fitness']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# ========================
# RISULTATI
# ========================
print("\n🎯 RISULTATI MODELLO:")
print("Accuracy:", round(accuracy_score(y_test, y_pred), 2))
print("\nConfusion Matrix:\n", confusion_matrix(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# ========================
# SALVATAGGIO MODELLO
# ========================
with open("fitness_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("\n✅ Modello salvato come 'fitness_model.pkl'")
