import requests
import json

BASE_URL = "http://10.49.12.39:5000/api/"

def validate_attempt(data: dict):
   
    endpoint = "attempt"
    url = BASE_URL + endpoint
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)

        print("Request successful" if response.status_code == 200 else "Request failed",
              "Status code:", response.status_code)

  
        try:
            return response.json()
        except ValueError:
            return {"error": "La respuesta no es JSON válido", "raw": response.text}

    except requests.exceptions.RequestException as e:
        return {"error": "Request error", "details": str(e)}
