import os

import psycopg2
import psycopg2.extras


def connect():
    """Connexion à PostgreSQL via des variables d'environnement."""
    conn = psycopg2.connect(
        dbname=os.environ.get("DB_NAME", "veterinaire"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        host=os.environ.get("DB_HOST", "localhost"),
        cursor_factory=psycopg2.extras.NamedTupleCursor,
    )
    conn.autocommit = True
    return conn
