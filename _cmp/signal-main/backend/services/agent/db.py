from models.database import get_connection


def get_db_connection():
    return get_connection()
