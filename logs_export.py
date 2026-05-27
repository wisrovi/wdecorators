"""Example: Export task logs via the API."""

import requests

headers = {"Authorization": "Bearer ADMIN_SECRET_KEY"}

python_task_code = """
def task_function():
    print("New task created from API running...")
"""

response = requests.post(
    "http://localhost:8000/execute_python_task/",
    json={
        "code": python_task_code,
        "interval": 7,
        "priority": "medium",
        "dynamic_interval": True,
    },
    headers=headers,
)

print("API response:", response.json())
