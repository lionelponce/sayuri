from datetime import date, time, datetime
from typing import List, Dict
import json, sqlite3
from sayuri.database import DataBase

class LLMLogs:
  def __init__(self):
    with DataBase() as database:
      database.cursor.execute("""
        CREATE TABLE IF NOT EXISTS llm_log (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          datetime TEXT,
          request TEXT NOT NULL,
          response TEXT NOT NULL
        );
        """)
      database.connection.commit()

  def save(self, request: Dict, response: Dict):
    now = datetime.now()
    
    request_string = json.dumps(request, ensure_ascii=False)
    response_string = json.dumps(response, ensure_ascii=False)
    
    with DataBase() as database:
      database.cursor.execute("INSERT INTO llm_log (datetime, request, response) VALUES (?, ?, ?)", (now.strftime("%Y-%m-%d %H:%M:%S"), request_string, response_string))
      database.connection.commit()
      return database.cursor.lastrowid
