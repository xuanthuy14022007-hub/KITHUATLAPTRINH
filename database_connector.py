import sqlite3

DB_NAME = 'nong_oi.db'

def get_connection():
    """Hàm duy nhất dùng để kết nối Database cho toàn bộ dự án"""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
