import sqlite3
from pathlib import Path

DB_PATH = Path("data/pointages.db")
DB_PATH.parent.mkdir(exist_ok=True, parents=True)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS pointages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            horodatage TEXT NOT NULL,
            type TEXT NOT NULL,
            salariee TEXT NOT NULL,
            client TEXT NOT NULL,
            lat REAL,
            lng REAL,
            precision REAL,
            distance INTEGER,
            statut TEXT,
            detail TEXT,
            verifie INTEGER DEFAULT 0
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS employes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL UNIQUE,
            taux_horaire REAL NOT NULL DEFAULT 0,
            actif INTEGER DEFAULT 1,
            notes TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS config_kv (
            cle TEXT PRIMARY KEY,
            valeur TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS planning (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employe TEXT NOT NULL,
            client TEXT NOT NULL,
            jour_semaine INTEGER NOT NULL,  -- 0=lundi ... 6=dimanche
            heure_debut TEXT NOT NULL,
            heure_fin TEXT NOT NULL,
            notes TEXT
        )
    """)

    # Seed initial : si aucun employé n'existe encore, on en crée deux par défaut
    # (reprend les anciens noms génériques de config.py) pour ne pas partir d'un
    # menu de pointage vide au premier lancement.
    count = conn.execute("SELECT COUNT(*) AS c FROM employes").fetchone()["c"]
    if count == 0:
        conn.execute("INSERT INTO employes (nom, taux_horaire, actif) VALUES (?, 0, 1)", ("Salariée 1",))
        conn.execute("INSERT INTO employes (nom, taux_horaire, actif) VALUES (?, 0, 1)", ("Salariée 2",))

    conn.commit()
    conn.close()


# ---------- Pointages ----------

def insert_pointage(horodatage, type_, salariee, client, lat, lng, precision, distance, statut, detail):
    conn = get_conn()
    conn.execute(
        """INSERT INTO pointages
           (horodatage, type, salariee, client, lat, lng, precision, distance, statut, detail, verifie)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)""",
        (horodatage, type_, salariee, client, lat, lng, precision, distance, statut, detail)
    )
    conn.commit()
    pointage_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return pointage_id


def get_pointages(limit=None, only_unverified_issues=False, mois=None):
    conn = get_conn()
    query = "SELECT * FROM pointages"
    clauses = []
    params = []
    if only_unverified_issues:
        clauses.append("(statut LIKE '%VÉRIFIER%' OR statut LIKE '%ERREUR%') AND verifie = 0")
    if mois:
        clauses.append("substr(horodatage,1,7) = ?")
        params.append(mois)
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY horodatage DESC"
    if limit:
        query += f" LIMIT {int(limit)}"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def set_verifie(pointage_id, value):
    conn = get_conn()
    conn.execute("UPDATE pointages SET verifie = ? WHERE id = ?", (1 if value else 0, pointage_id))
    conn.commit()
    conn.close()


def get_pointage(pid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM pointages WHERE id = ?", (pid,)).fetchone()
    conn.close()
    return row


def update_pointage(pid, horodatage, type_, salariee, client, statut, detail, verifie):
    conn = get_conn()
    conn.execute(
        """UPDATE pointages SET horodatage=?, type=?, salariee=?, client=?, statut=?, detail=?, verifie=?
           WHERE id=?""",
        (horodatage, type_, salariee, client, statut, detail, 1 if verifie else 0, pid)
    )
    conn.commit()
    conn.close()


# ---------- Employés ----------

def get_employes(only_actifs=False):
    conn = get_conn()
    q = "SELECT * FROM employes"
    if only_actifs:
        q += " WHERE actif = 1"
    q += " ORDER BY nom"
    rows = conn.execute(q).fetchall()
    conn.close()
    return rows


def get_employe(emp_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM employes WHERE id = ?", (emp_id,)).fetchone()
    conn.close()
    return row


def add_employe(nom, taux_horaire, notes=""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO employes (nom, taux_horaire, actif, notes) VALUES (?, ?, 1, ?)",
        (nom, taux_horaire, notes)
    )
    conn.commit()
    conn.close()


def update_employe(emp_id, nom, taux_horaire, notes, actif):
    conn = get_conn()
    conn.execute(
        "UPDATE employes SET nom = ?, taux_horaire = ?, notes = ?, actif = ? WHERE id = ?",
        (nom, taux_horaire, notes, 1 if actif else 0, emp_id)
    )
    conn.commit()
    conn.close()


def delete_employe(emp_id):
    conn = get_conn()
    conn.execute("DELETE FROM employes WHERE id = ?", (emp_id,))
    conn.commit()
    conn.close()


# ---------- Config clé/valeur (consignes, bandeau) ----------

def get_kv(cle, defaut=""):
    conn = get_conn()
    row = conn.execute("SELECT valeur FROM config_kv WHERE cle = ?", (cle,)).fetchone()
    conn.close()
    return row["valeur"] if row else defaut


def set_kv(cle, valeur):
    conn = get_conn()
    conn.execute(
        """INSERT INTO config_kv (cle, valeur) VALUES (?, ?)
           ON CONFLICT(cle) DO UPDATE SET valeur = excluded.valeur""",
        (cle, valeur)
    )
    conn.commit()
    conn.close()


# ---------- Planning ----------

def get_planning():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM planning ORDER BY jour_semaine, heure_debut").fetchall()
    conn.close()
    return rows


def get_planning_item(pid):
    conn = get_conn()
    row = conn.execute("SELECT * FROM planning WHERE id = ?", (pid,)).fetchone()
    conn.close()
    return row


def add_planning(employe, client, jour_semaine, heure_debut, heure_fin, notes=""):
    conn = get_conn()
    conn.execute(
        "INSERT INTO planning (employe, client, jour_semaine, heure_debut, heure_fin, notes) VALUES (?, ?, ?, ?, ?, ?)",
        (employe, client, jour_semaine, heure_debut, heure_fin, notes)
    )
    conn.commit()
    conn.close()


def update_planning(pid, employe, client, jour_semaine, heure_debut, heure_fin, notes):
    conn = get_conn()
    conn.execute(
        """UPDATE planning SET employe=?, client=?, jour_semaine=?, heure_debut=?, heure_fin=?, notes=?
           WHERE id=?""",
        (employe, client, jour_semaine, heure_debut, heure_fin, notes, pid)
    )
    conn.commit()
    conn.close()


def delete_planning(pid):
    conn = get_conn()
    conn.execute("DELETE FROM planning WHERE id = ?", (pid,))
    conn.commit()
    conn.close()
