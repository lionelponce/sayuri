from datetime import date, time, datetime
import requests
import json

def generate( data: str, model: str, api_key: str):
  with open('./logs/googleapis.log', 'a', encoding='utf-8') as log:
    log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - request:\n{data}\n{model}\n{api_key}\n\n")

  url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
  
  try:
    response = requests.post(url, headers={'Content-Type': 'application/json'}, json=data)
    response.raise_for_status()

    with open('./logs/googleapis.log', 'a', encoding='utf-8') as log:
      log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - response:\n{json.loads(response.text)}\n\n")

    return json.loads(response.text)
  
  except requests.exceptions.RequestException as e:
    return {"error": f"Error en la petición: {str(e)}"}

"""
Ejemplo de uso:

data = {
  "contents": [
    {
      "parts":[
        {
          "text": "Hola, ¿cómo estás?"
        }
      ]
    }
  ]
}

response = generate(data)

print(response)
"""