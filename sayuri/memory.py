from datetime import date, time, datetime
from typing import List, Dict
import json, sqlite3
from sayuri.database import DataBase

class Memory:
  def __init__(self):
    with DataBase() as database:
      database.cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          created_at TEXT NOT NULL,
          last_used TEXT,
          scope TEXT NOT NULL,       -- usuario | proyecto | sistema
          level TEXT NOT NULL,       -- corto | medio | largo
          content TEXT NOT NULL,
          importance INTEGER NOT NULL, -- 1 | 2 | 3
          tags TEXT NOT NULL,        -- JSON array
          source TEXT NOT NULL,      -- conversacion | sistema | usuario
          reason TEXT
        );
        """)
      database.connection.commit()
    
  def save(self, scope: str, level: str, content: str, importance: int, tags: List[str], source: str, reason: str):
    now = datetime.now()
    with DataBase() as database:
      database.cursor.execute("INSERT INTO memory (created_at, scope, content, importance, level, tags, reason, source) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                              (now.strftime("%Y-%m-%d %H:%M:%S"), scope, content, importance, level, json.dumps(tags), reason, source))
      database.connection.commit()
      return database.cursor.lastrowid
  
  def get(self) -> List[sqlite3.Row]:
    with DataBase() as database:
      database.cursor.execute("SELECT * FROM memory")
      return database.cursor.fetchall()

  def select(self, scopes: List[str], importance: int = 2, limit: int = 5) -> List[Dict]:    
    with DataBase() as database:
      database.cursor.execute("""
        SELECT *
          FROM memory
          WHERE scope IN ({})
          AND importance >= ?
          ORDER BY importance DESC, last_used ASC
          LIMIT ?
        """.format(",".join("?" * len(scopes))),
        (*scopes, importance, limit))
      rows = database.cursor.fetchall()

    memories = []
    for row in rows:
      memories.append({
        "id": row["id"],
        "content": row["content"],
        "scope": row["scope"],
        "level": row["level"],
        "importance": row["importance"],
        "tags": json.loads(row["tags"]),
        "reason": row["reason"]
      })

    return memories
