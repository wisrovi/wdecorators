import requests
import json

headers = {"Authorization": "Bearer ADMIN_SECRET_KEY"}

python_task_code = """
def new_task():
    print("Nueva tarea creada desde la API ejecutándose...")
"""

response = requests.post("http://localhost:8000/execute_python_task/", json={
    "code": python_task_code,
    "interval": 7,
    "priority": "media",
    "dynamic_interval": True
}, headers=headers)

print("Respuesta API:", response.json())
