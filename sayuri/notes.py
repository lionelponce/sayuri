from datetime import date, time, datetime
from typing import List, Dict
import json, sqlite3
from sayuri.database import DataBase

class Notes:
  def __init__(self):
    with DataBase() as database:
      database.cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          created_at INTEGER NOT NULL,
          updated_at INTEGER,
          deleted_at INTEGER,
          title TEXT NOT NULL,
          content TEXT NOT NULL,
          category TEXT,
          priority INTEGER DEFAULT 0,
          status TEXT DEFAULT 'active',
          tags TEXT DEFAULT '[]'
        );
        """)
      database.connection.commit()
  
  def save(self, title: str, content: str, category: str, priority: int, status: str, tags: List[str]):
    now = datetime.now()
    with DataBase() as database:
      database.cursor.execute("INSERT INTO notes (created_at, title, content, category, priority, status, tags) VALUES (?, ?, ?, ?, ?, ?, ?)", (now.strftime("%Y-%m-%d %H:%M:%S"), title, content, category, priority, status, tags))
      database.connection.commit()
      return database.cursor.lastrowid
  
  def get(self) -> List[sqlite3.Row]:
    with DataBase() as database:
      database.cursor.execute("SELECT * FROM notes")
      return self.cursor.fetchall()
