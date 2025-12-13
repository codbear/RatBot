# utils/db.py
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

# Récupérer l'URL de connexion depuis les variables d'environnement (Railway fournit DATABASE_URL)
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL non défini. Vérifie tes variables d'environnement sur Railway.")

# Connexion globale
def get_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

# Initialisation de la base (à appeler lors du démarrage)
def init_db():
    conn = get_connection()
    with conn:
        with conn.cursor() as cur:
            # Table des voyages
            cur.execute(
                '''
                CREATE TABLE IF NOT EXISTS voyages (
                    id SERIAL PRIMARY KEY,
                    gold INTEGER NOT NULL,
                    emissary_value INTEGER NOT NULL,
                    duration INTEGER NOT NULL,
                    members BIGINT[] NOT NULL,
                    author BIGINT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    season VARCHAR(100) NOT NULL
                )
                '''
            )
            # Table des saisons
            cur.execute(
                '''
                CREATE TABLE IF NOT EXISTS seasons (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    start_date TIMESTAMP NOT NULL,
                    end_date TIMESTAMP,
                    is_active BOOLEAN NOT NULL DEFAULT FALSE
                )
                '''
            )
    conn.close()

# Enregistrement d'un voyage
def insert_voyage(voyage: dict) -> int:
    """
    Insert a voyage and return the generated id.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO voyages (gold, emissary_value, duration, members, author, timestamp, season)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        voyage['gold'],
                        voyage['emissary_value'],
                        voyage['duration'],
                        voyage['members'],
                        voyage['author'],
                        voyage['timestamp'],
                        voyage['season']
                    )
                )
                new_id = cur.fetchone()['id']
                return new_id
    finally:
        conn.close()

# Récupération des voyages d'une saison
def fetch_voyages(season_name: str) -> list[dict]:
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM voyages WHERE season = %s ORDER BY id",
                    (season_name,)
                )
                return cur.fetchall()
    finally:
        conn.close()

# Récupération d'un voyage par ID
def get_voyage(id: int) -> dict | None:
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM voyages WHERE id = %s",
                    (id,)
                )
                return cur.fetchone()
    finally:
        conn.close()


# Suppression d'un voyage
def delete_voyage(season_name: str, voyage_id: int) -> bool:
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM voyages WHERE season = %s AND id = %s",
                    (season_name, voyage_id)
                )
                return cur.rowcount > 0
    finally:
        conn.close()

# Mise à jour d'un voyage
def update_voyage(voyage: dict) -> bool:
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE voyages SET gold = %s, emissary_value = %s, duration = %s, members = %s WHERE season = %s AND id = %s",
                    (voyage['gold'], voyage['emissary_value'], voyage['duration'], voyage['members'], voyage['season'], voyage['id'])
                )
                return cur.rowcount > 0
    finally:
        conn.close()

# === GESTION DES SAISONS ===

# Démarrer une nouvelle saison
def start_season(season_name: str) -> int:
    """
    Démarre une nouvelle saison et désactive l'ancienne.
    Retourne l'ID de la nouvelle saison créée.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                # Désactiver toutes les saisons existantes
                cur.execute("UPDATE seasons SET is_active = FALSE")
                
                # Créer la nouvelle saison
                cur.execute(
                    """
                    INSERT INTO seasons (name, start_date, is_active)
                    VALUES (%s, NOW(), TRUE)
                    RETURNING id
                    """,
                    (season_name,)
                )
                new_id = cur.fetchone()['id']
                return new_id
    finally:
        conn.close()

# Terminer la saison en cours
def end_current_season() -> bool:
    """
    Termine la saison actuellement active.
    Retourne True si une saison a été terminée, False sinon.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE seasons SET is_active = FALSE, end_date = NOW() WHERE is_active = TRUE"
                )
                return cur.rowcount > 0
    finally:
        conn.close()

# Récupérer la saison active
def get_active_season() -> dict | None:
    """
    Récupère la saison actuellement active.
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM seasons WHERE is_active = TRUE LIMIT 1"
                )
                return cur.fetchone()
    finally:
        conn.close()

# Récupérer toutes les saisons
def get_all_seasons() -> list[dict]:
    """
    Récupère toutes les saisons, triées par date de début (plus récente en premier).
    """
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM seasons ORDER BY start_date DESC"
                )
                return cur.fetchall()
    finally:
        conn.close()
