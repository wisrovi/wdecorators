import sqlite3
import time
import psutil
import threading
from datetime import datetime
import functools
import json
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import jwt
import socket

# Configuración de autenticación (clave secreta para JWT)
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ADMIN_TOKEN = jwt.encode({"role": "admin"}, SECRET_KEY, algorithm=ALGORITHM)

# Archivo de base de datos SQLite
DB_FILE = "task_logs_v14.db"

class DatabaseHandler:
    """Maneja la conexión con SQLite y PostgreSQL, usando lock para serializar operaciones."""
    def __init__(self, db_config=None):
        self.use_postgres = False
        self.lock = threading.Lock()
        
        if db_config:
            try:
                import psycopg2
                self.conn = psycopg2.connect(**db_config)
                self.use_postgres = True
                print("Conectado a PostgreSQL.")
            except Exception as e:
                print(f"Error con PostgreSQL: {e}. Usando SQLite.")
                self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
            self.cursor = self.conn.cursor()  # Cursor no se usará directamente
        else:
            self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
            self.cursor = self.conn.cursor()
            print("Usando SQLite.")
        
        self.setup_database()

    def setup_database(self):
        """Crea las tablas necesarias."""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                task_name TEXT,
                message TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                interval INTEGER,
                priority TEXT,
                status TEXT,
                max_executions INTEGER,
                current_executions INTEGER,
                dynamic_interval BOOLEAN,
                adaptive_priority BOOLEAN,
                dependent_task TEXT,
                enable_api BOOLEAN
            )
            """
        ]
        with self.lock:
            cur = self.conn.cursor()
            for query in queries:
                cur.execute(query)
            self.conn.commit()
            cur.close()

    def execute(self, query, params=()):
        """Ejecuta una consulta en la base de datos usando un cursor nuevo."""
        with self.lock:
            cur = self.conn.cursor()
            cur.execute(query, params)
            self.conn.commit()
            cur.close()

    def fetch_all(self, query, params=()):
        """Obtiene todos los resultados usando un cursor nuevo."""
        with self.lock:
            cur = self.conn.cursor()
            cur.execute(query, params)
            results = cur.fetchall()
            cur.close()
            return results

class Periodic_task_sched:
    """Clase para manejar tareas periódicas con decoradores, API opcional y panel de control."""
    _api_running = False  # Evitar múltiples inicios de la API

    def __init__(self):
        self.database = None
        self.executors = {}
        self.api_enabled = False
        self.api_app = FastAPI()

        # Montar archivos estáticos y plantillas HTML
        self.api_app.mount("/static", StaticFiles(directory="static"), name="static")
        self.templates = Jinja2Templates(directory="templates")

        # Panel Web de Administración con métricas en tiempo real
        @self.api_app.get("/", response_class=HTMLResponse)
        def dashboard(request: Request):
            tasks = list(self.executors.keys())
            logs = self.database.fetch_all("SELECT * FROM logs ORDER BY timestamp DESC LIMIT 50")
            return self.templates.TemplateResponse("dashboard.html", {"request": request, "tasks": tasks, "logs": logs})

        # Rutas API protegidas (usando Form para recibir datos de formularios)
        @self.api_app.post("/list_tasks/")
        def list_tasks(token: str = Form(...)):
            self.verify_admin(token)
            return list(self.executors.keys())

        @self.api_app.post("/pause_task/")
        def pause_task(task_name: str = Form(...), token: str = Form(...)):
            self.verify_admin(token)
            if task_name in self.executors:
                self.executors[task_name].pause()
                return {"status": f"Tarea {task_name} pausada."}
            return {"error": f"Tarea {task_name} no encontrada."}

        @self.api_app.post("/resume_task/")
        def resume_task(task_name: str = Form(...), token: str = Form(...)):
            self.verify_admin(token)
            if task_name in self.executors:
                self.executors[task_name].resume()
                return {"status": f"Tarea {task_name} reanudada."}
            return {"error": f"Tarea {task_name} no encontrada."}

        @self.api_app.post("/stop_task/")
        def stop_task(task_name: str = Form(...), token: str = Form(...)):
            self.verify_admin(token)
            if task_name in self.executors:
                self.executors[task_name].stop()
                return {"status": f"Tarea {task_name} detenida."}
            return {"error": f"Tarea {task_name} no encontrada."}

        # Protección contra código malicioso: Ejecuta código Python para crear tareas
        @self.api_app.post("/execute_python_task/")
        def execute_python_task(task_code: str = Form(...), interval: int = Form(...), priority: str = Form(...), token: str = Form(...)):
            self.verify_admin(token)
            exec_globals = {}
            safe_env = {"print": print, "range": range, "len": len}
            try:
                exec(task_code, safe_env, exec_globals)
                if "task_function" in exec_globals:
                    new_task = self.periodic_execution(interval, priority)(exec_globals["task_function"])
                    new_task()
                    return {"status": "Nueva tarea creada y en ejecución."}
                return {"error": "No se encontró 'task_function' en el código proporcionado."}
            except Exception as e:
                return {"error": str(e)}
            
        # Ruta para mostrar el formulario de login
        @self.api_app.get("/login", response_class=HTMLResponse)
        def login_page(request: Request):
            return self.templates.TemplateResponse("login.html", {"request": request})

        # Ruta para procesar el login y devolver el token
        @self.api_app.post("/login")
        async def login(request: Request):
            form_data = await request.form()
            username = form_data.get("username")
            password = form_data.get("password")
            
            # Aquí definimos la lógica de autenticación.
            # Por ejemplo, para efectos de prueba:
            if username == "admin" and password == "admin":
                role = "admin"
            else:
                # Si no es admin, se asigna rol de supervisor (o se rechaza el login según tus requisitos)
                role = "supervisor"
            
            token = jwt.encode({"role": role}, SECRET_KEY, algorithm=ALGORITHM)
            # Redireccionar al dashboard incluyendo el token en la URL o devolverlo en la respuesta.
            # Aquí devolvemos el token en una respuesta JSON para simplicidad.
            return {"token": token}

    def verify_admin(self, token: str):
        """Verifica si el usuario es administrador o supervisor (por defecto, sin login, es supervisor)."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload["role"] not in ["admin", "supervisor"]:
                raise HTTPException(status_code=403, detail="Acceso denegado.")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Token inválido.")
        return token

    def set_database(self, db_config_json=None):
        """Configura la base de datos (SQLite o PostgreSQL)."""
        db_config = json.loads(db_config_json) if db_config_json else None
        self.database = DatabaseHandler(db_config)

    def periodic_execution(self, interval, priority="media", max_executions=None, dynamic_interval=False, adaptive_priority=False, dependent_task=None, enable_api=False):
        """Decorador para manejar tareas periódicas con configuración avanzada."""
        if enable_api:
            self.api_enabled = True

        def decorator(func):
            executor = self.PeriodicExecutor(func, interval, priority, max_executions, dynamic_interval, adaptive_priority, dependent_task, enable_api, self.database)
            self.executors[func.__name__] = executor

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                executor.start(*args, **kwargs)
                return executor
            return wrapper
        return decorator

    def is_port_in_use(self, port=8000):
        """Verifica si el puerto ya está en uso."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0

    def start_api(self):
        """Inicia la API solo si es requerida y no está en ejecución."""
        if self.api_enabled and not self.is_port_in_use():
            if not Periodic_task_sched._api_running:
                print("Iniciando API en http://localhost:8000")
                Periodic_task_sched._api_running = True
                threading.Thread(target=uvicorn.run, args=(self.api_app,), kwargs={"host": "0.0.0.0", "port": 8000}, daemon=True).start()
        else:
            print("La API ya está en ejecución en otro proceso. Se reutiliza la instancia existente.")

    class PeriodicExecutor:
        """Ejecutor de tareas periódicas con prioridad inteligente y dependencias."""
        def __init__(self, func, interval, priority, max_executions, dynamic_interval, adaptive_priority, dependent_task, enable_api, database):
            self.func = func
            self.interval = interval
            self.priority = priority
            self.max_executions = max_executions or float("inf")
            self.execution_count = 0
            self.running = False
            self.paused = False
            self.dynamic_interval = dynamic_interval
            self.adaptive_priority = adaptive_priority
            self.dependent_task = dependent_task
            self.enable_api = enable_api
            self.database = database

            self._save_task()

        def _save_task(self):
            """Guarda la tarea en la base de datos."""
            self.database.execute(
                "INSERT OR IGNORE INTO tasks (name, interval, priority, status, max_executions, current_executions, dynamic_interval, adaptive_priority, dependent_task, enable_api) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (self.func.__name__, self.interval, self.priority, "stopped", self.max_executions, 0, self.dynamic_interval, self.adaptive_priority, self.dependent_task, self.enable_api)
            )

        def start(self):
            """Inicia la ejecución de la tarea."""
            if not self.running:
                self.running = True
                threading.Thread(target=self._run).start()

        def _run(self):
            """Ejecuta la tarea según configuraciones."""
            while self.running and self.execution_count < self.max_executions:
                if self.paused:
                    time.sleep(1)
                    continue

                # Si existe dependencia, verificar que la tarea dependiente esté completada
                if self.dependent_task:
                    result = self.database.fetch_all("SELECT status FROM tasks WHERE name = ?", (self.dependent_task,))
                    if result and result[0][0] != "completed":
                        time.sleep(self.interval)
                        continue

                self.func()
                self.execution_count += 1

                self.database.execute(
                    "INSERT INTO logs (timestamp, task_name, message) VALUES (?, ?, ?)",
                    (datetime.now().isoformat(), self.func.__name__, f"Ejecutado {self.execution_count} veces.")
                )
                self.database.execute(
                    "UPDATE tasks SET status = 'completed' WHERE name = ?",
                    (self.func.__name__,)
                )
                time.sleep(self.interval)
            self.running = False

        def stop(self):
            """Detiene la ejecución de la tarea."""
            self.running = False

        def pause(self):
            """Pausa temporalmente la ejecución de la tarea."""
            self.paused = True

        def resume(self):
            """Reanuda la tarea pausada."""
            self.paused = False
