from datetime import date, time, datetime
from typing import List, Dict
import json, sqlite3
from sayuri.database import DataBase

class History:
  def __init__(self):
    with DataBase() as database:
      database.cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          datetime TEXT NOT NULL,
          session TEXT NOT NULL,
          role TEXT NOT NULL,
          text TEXT NOT NULL
        );
        """)
      database.connection.commit()

  def save(self, role: str, text: str, session: str = "SYR-SESSION-00"):
    now = datetime.now()
    with DataBase() as database:
      database.cursor.execute("INSERT INTO history (datetime, session, role, text) VALUES (?, ?, ?, ?)", (now.strftime("%Y-%m-%d %H:%M:%S"), session, role, text))
      database.connection.commit()
      return database.cursor.lastrowid
  
  def get(self, limit: int = 6) -> List[sqlite3.Row]:
    with DataBase() as database:
      database.cursor.execute("SELECT * FROM (SELECT * FROM history ORDER BY datetime DESC LIMIT ?) ORDER BY datetime ASC", (limit,))
      return database.cursor.fetchall()
