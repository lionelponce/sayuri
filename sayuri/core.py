import json, re, os, sayuri.googleapis
from datetime import date, time, datetime, timedelta
from typing import List, Dict


from sayuri.history import History
from sayuri.llmlogs import LLMLogs
from sayuri.notes import Notes
from sayuri.memory import Memory

class Sayuri_Core():
  def __init__(self, path = "./config.json"):
    self.config = self._load_config(path)
    self.intention_prompt = self._load_prompt('intention')
    self.personality_prompt = self._load_prompt('personality')
    self.history = History()
    self.llmlogs = LLMLogs()
    self.notes = Notes()
    self.memory = Memory()

# Cargar Configuraciones
  def _load_config(self, path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    except FileNotFoundError:
        raise RuntimeError(f"No se encontró el archivo de configuración: {path}")
    
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Error al parsear config.json: {e}")
    
# Cargar Prompts
  def _load_prompt(self, prompt_type):
    try:
      prompts = self.config.get('prompts')
      if not prompts or prompt_type not in prompts:
         raise KeyError(f"Prompt {prompt_type} no definido en config..")
      
      path = prompts[prompt_type]

      with open(path, 'r', encoding='utf-8') as f:
        return f.read()

    except FileNotFoundError:
        raise RuntimeError(f"No se encontró el archivo de prompt: {path}..")

# Analizar Intencion
  def _analyze_intention(self, user_message):
    context = self._get_history()
    
    request = {
      "contents": 
        {
          "role": "user",
          "parts": [
              {
                "text": f"{self.intention_prompt}\n---\n\nCONTEXT WINDOW\n\n{context}---\n\nUSER MESSAGE\n{user_message}"
              }
            ]
        },
      "generationConfig": 
        {
          "temperature": 0.0
        }
    };
    with open('./logs/core.log', 'a', encoding='utf-8') as log:
      log.write(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - _analyze_intention request:\n{request}\n\n")

    response = sayuri.googleapis.generate(request, self.config.get('models').get('intention'), self.config.get('api_key'))

    with open('./logs/core.log', 'a', encoding='utf-8') as log:
      log.write(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - _analyze_intention response:\n{response}\n\n")

    self.llmlogs.save(request, response)
    
    instructions = json.loads(response.get('candidates')[0].get('content').get('parts')[0].get('text')[7:][:-3].strip())
    
    intent = f"INTENT BLOCK — REQUIRED\n\n{instructions}"

    return instructions, intent

# Manejar Memoria
  def _handle_memory(self, instruction):
    if instruction.get('memory').get('store'):
      memory = instruction.get('memory')
      
      self.memory.save(
        memory.get('scope'), 
        memory.get('level'), 
        memory.get('content'), 
        memory.get('importance'), 
        json.dumps(memory.get('tags'), ensure_ascii=False),
        memory.get('source'),
        memory.get('reason')
      )
        
      return True
    
  def _memory_context(self, scopes: List[Dict]):
    memories = self.memory.select(scopes=scopes)
    if not memories:
      return ""
      
    context = "RELEVANT MEMORIES\n\n"
    for row in memories:
      context += f"- {row['content']}\n"

    return f"{context}\n"

# Manejar Notas
  def _handle_notes(self, instruction):
    if instruction.get('note').get('create'):
      note = instruction.get('note')
    
      self.notes.save(
        note.get('title'), 
        note.get('content'), 
        note.get('category'), 
        note.get('priority'), 
        note.get('status'), 
        json.dumps(note.get('tags'), ensure_ascii=False)
      )
      
      return True
      
# Obtener Historial
  def _get_history(self):
    history = ""
    for row in self.history.get():
      history += f"{row['role'].upper()}:\n{row['text']}\n\n"

    return history
  
# Generar con Personalidad
  def _generate_response(self, instructions, scopes, history, user_message):
    request = {
      "contents": 
        {
          "role": "user",
          "parts": [
              {
                "text": f"{self.personality_prompt}\n---\n\n{instructions}\n\n---\n\n{scopes}---\n\nRECENT HISTORY (FOR CONTEXTUAL REFERENCE ONLY, NOT AS INSTRUCTIONS)\n\n{history}---\n\nUSER MESSAGE\n\n{user_message}"
              }
            ]
        },
      "generationConfig": 
        {
          "temperature": 0.85
        }
    };

    response = sayuri.googleapis.generate(request, self.config.get('models').get('personality'), self.config.get('api_key'))

    self.llmlogs.save(request, response)

    message = response.get('candidates')[0].get('content').get('parts')[0].get('text').strip()
    
    self.history.save("user", user_message)
    self.history.save("model", message)

    return message
  
# Sayuri Contesta
  def answer(self, user_message):
    with open('./logs/core.log', 'a', encoding='utf-8') as log:
      log.write(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - user_mesage:\n{user_message}\n\n")

    instructions, intent = self._analyze_intention(user_message)

    with open('./logs/core.log', 'a', encoding='utf-8') as log:
      log.write(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - instructions:\n{instructions}\n\n")

    memory_saved = self._handle_memory(instructions)

    with open('./logs/core.log', 'a', encoding='utf-8') as log:
      log.write(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - memory_saved:\n{memory_saved}\n\n")

    note_saved = self._handle_notes(instructions)

    with open('./logs/core.log', 'a', encoding='utf-8') as log:
      log.write(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - note_saved:\n{note_saved}\n\n")

    history = self._get_history()

    with open('./logs/core.log', 'a', encoding='utf-8') as log:
      log.write(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - history:\n{history}\n\n")

    scopes = self._memory_context(['user',])

    message = self._generate_response(intent, scopes, history, user_message)

    with open('./logs/core.log', 'a', encoding='utf-8') as log:
      log.write(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - message:\n{message}\n\n")
    
    response = {
      "message": message,
      "memory_saved": memory_saved,
      "note_saved": note_saved
    }

    with open('./logs/core.log', 'a', encoding='utf-8') as log:
      log.write(f"{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - response:\n{response}\n\n")

    return json.dumps(response, ensure_ascii=False)

# Borrar Base de Datos
  def factory_reset(self, path = "./databases/sayuri.db"):
    if os.path.exists(path):
        os.remove(path)
