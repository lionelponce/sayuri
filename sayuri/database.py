import sqlite3

class DataBase:
  def __init__(self, database: str = "./databases/sayuri.db"):
    self.database = database
  
  def __enter__(self):
    self.connection = sqlite3.connect(self.database)
    self.connection.row_factory = sqlite3.Row # Establece que las filas retornadas por las consultas sean objetos lugar de tuplas. row['name']
    self.cursor = self.connection.cursor()
    return self
  
  def __exit__(self, exc_type, exc_val, exc_tb):
    self.connection.close()
