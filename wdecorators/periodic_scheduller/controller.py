"""Periodic task scheduler with FastAPI dashboard and database persistence."""

import json
import socket
import sqlite3
import threading
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
DB_FILE = "task_logs_v14.db"


class DatabaseHandler:
    """Manages SQLite (or PostgreSQL) connections with thread-safe operations."""

    def __init__(self, db_config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize database connection.

        Args:
            db_config: Optional PostgreSQL connection parameters.
                       If None, uses SQLite.
        """
        self.use_postgres = False
        self.lock = threading.Lock()

        if db_config:
            try:
                import psycopg2  # type: ignore

                self.conn = psycopg2.connect(**db_config)
                self.use_postgres = True
                print("Connected to PostgreSQL.")
            except Exception as e:
                print(f"PostgreSQL connection failed: {e}. Falling back to SQLite.")
                self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        else:
            self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
            print("Using SQLite.")

        self._setup_database()

    def _setup_database(self) -> None:
        """Create required tables if they do not exist."""
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
            """,
        ]
        with self.lock:
            cur = self.conn.cursor()
            for query in queries:
                cur.execute(query)
            self.conn.commit()
            cur.close()

    def execute(self, query: str, params: Tuple = ()) -> None:
        """Execute a write query with thread safety.

        Args:
            query: SQL query string.
            params: Query parameters.
        """
        with self.lock:
            cur = self.conn.cursor()
            cur.execute(query, params)
            self.conn.commit()
            cur.close()

    def fetch_all(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Execute a read query and return all results.

        Args:
            query: SQL query string.
            params: Query parameters.

        Returns:
            List of result rows.
        """
        with self.lock:
            cur = self.conn.cursor()
            cur.execute(query, params)
            results = cur.fetchall()
            cur.close()
            return results


class Periodic_task_sched:
    """Periodic task scheduler with decorator-based registration and
    optional API dashboard.

    Usage:
        controller = Periodic_task_sched()
        controller.set_database()

        @controller.periodic_execution(interval=5)
        def my_task():
            print("Running...")

        my_task()
        controller.start_api()
    """

    _api_running = False

    def __init__(self) -> None:
        """Initialize the scheduler."""
        self.database: Optional[DatabaseHandler] = None
        self.executors: Dict[str, "Periodic_task_sched.PeriodicExecutor"] = {}
        self.api_enabled = False
        self.api_app = None

    def _build_api_app(self):
        """Lazily build the FastAPI application with dashboard routes."""
        try:
            import jwt  # type: ignore
            import uvicorn  # type: ignore
            from fastapi import FastAPI, Form, HTTPException, Request
            from fastapi.responses import HTMLResponse
            from fastapi.staticfiles import StaticFiles
            from fastapi.templating import Jinja2Templates
        except ImportError as e:
            raise ImportError(
                "Periodic_task_sched API requires: fastapi, uvicorn, "
                f"pyjwt, jinja2, python-multipart. Missing: {e}"
            )

        self.api_app = FastAPI()

        self.api_app.mount("/static", StaticFiles(directory="static"), name="static")
        self.templates = Jinja2Templates(directory="templates")

        @self.api_app.get("/", response_class=HTMLResponse)
        def dashboard(request: Request):
            tasks = list(self.executors.keys())
            logs = []
            if self.database:
                logs = self.database.fetch_all(
                    "SELECT * FROM logs ORDER BY timestamp DESC LIMIT 50"
                )
            return self.templates.TemplateResponse(
                "dashboard.html", {"request": request, "tasks": tasks, "logs": logs}
            )

        @self.api_app.post("/list_tasks/")
        def list_tasks(token: str = Form(...)):
            self.verify_admin(token)
            return list(self.executors.keys())

        @self.api_app.post("/pause_task/")
        def pause_task(task_name: str = Form(...), token: str = Form(...)):
            self.verify_admin(token)
            if task_name in self.executors:
                self.executors[task_name].pause()
                return {"status": f"Task '{task_name}' paused."}
            return {"error": f"Task '{task_name}' not found."}

        @self.api_app.post("/resume_task/")
        def resume_task(task_name: str = Form(...), token: str = Form(...)):
            self.verify_admin(token)
            if task_name in self.executors:
                self.executors[task_name].resume()
                return {"status": f"Task '{task_name}' resumed."}
            return {"error": f"Task '{task_name}' not found."}

        @self.api_app.post("/stop_task/")
        def stop_task(task_name: str = Form(...), token: str = Form(...)):
            self.verify_admin(token)
            if task_name in self.executors:
                self.executors[task_name].stop()
                return {"status": f"Task '{task_name}' stopped."}
            return {"error": f"Task '{task_name}' not found."}

        @self.api_app.post("/execute_python_task/")
        def execute_python_task(
            task_code: str = Form(...),
            interval: int = Form(...),
            priority: str = Form(...),
            token: str = Form(...),
        ):
            self.verify_admin(token)
            exec_globals: Dict[str, Any] = {}
            safe_env = {"print": print, "range": range, "len": len}
            try:
                exec(task_code, safe_env, exec_globals)
                if "task_function" in exec_globals:
                    new_task = self.periodic_execution(interval, priority)(
                        exec_globals["task_function"]
                    )
                    new_task()
                    return {"status": "New task created and running."}
                return {"error": "'task_function' not found in provided code."}
            except Exception as e:
                return {"error": str(e)}

        @self.api_app.get("/login", response_class=HTMLResponse)
        def login_page(request: Request):
            return self.templates.TemplateResponse("login.html", {"request": request})

        @self.api_app.post("/login")
        async def login(request: Request):
            form_data = await request.form()
            username = form_data.get("username")
            password = form_data.get("password")

            if username == "admin" and password == "admin":
                role = "admin"
            else:
                role = "supervisor"

            token = jwt.encode({"role": role}, SECRET_KEY, algorithm=ALGORITHM)
            return {"token": token}

    def verify_admin(self, token: str) -> str:
        """Verify JWT token has admin or supervisor role.

        Args:
            token: JWT token string.

        Returns:
            The verified token.

        Raises:
            HTTPException: If token is invalid or role is unauthorized.
        """
        try:
            import jwt  # type: ignore
            from fastapi import HTTPException
        except ImportError as e:
            raise ImportError("verify_admin requires: pyjwt, fastapi. " f"Missing: {e}")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload["role"] not in ["admin", "supervisor"]:
                raise HTTPException(status_code=403, detail="Access denied.")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token.")
        return token

    def set_database(self, db_config_json: Optional[str] = None) -> None:
        """Configure the database backend.

        Args:
            db_config_json: Optional JSON string with PostgreSQL config.
        """
        db_config = json.loads(db_config_json) if db_config_json else None
        self.database = DatabaseHandler(db_config)

    def periodic_execution(
        self,
        interval: int,
        priority: str = "medium",
        max_executions: Optional[int] = None,
        dynamic_interval: bool = False,
        adaptive_priority: bool = False,
        dependent_task: Optional[str] = None,
        enable_api: bool = False,
    ):
        """Register a function as a periodic task via decorator.

        Args:
            interval: Execution interval in seconds.
            priority: Task priority ('low', 'medium', 'high').
            max_executions: Max executions (None = unlimited).
            dynamic_interval: Allow dynamic interval adjustment.
            adaptive_priority: Allow adaptive priority.
            dependent_task: Name of task this one depends on.
            enable_api: Enable the API dashboard for this task.

        Returns:
            Decorator that wraps the task function.
        """
        if enable_api:
            self.api_enabled = True

        def decorator(func: Callable) -> Callable:
            executor = self.PeriodicExecutor(
                func=func,
                interval=interval,
                priority=priority,
                max_executions=max_executions,
                dynamic_interval=dynamic_interval,
                adaptive_priority=adaptive_priority,
                dependent_task=dependent_task,
                enable_api=enable_api,
                database=self.database,
            )
            self.executors[func.__name__] = executor

            def wrapper(*args: Any, **kwargs: Any) -> "PeriodicExecutor":
                executor.start()
                return executor

            return wrapper

        return decorator

    @staticmethod
    def is_port_in_use(port: int = 8000) -> bool:
        """Check if a network port is in use.

        Args:
            port: Port number to check.

        Returns:
            True if the port is in use, False otherwise.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0

    def start_api(self) -> None:
        """Start the FastAPI dashboard server in a background thread."""
        if not self.api_enabled:
            print("API not enabled. Set enable_api=True on a task.")
            return
        if self.is_port_in_use():
            print("API already running on port 8000.")
            return

        if self.api_app is None:
            self._build_api_app()

        if not Periodic_task_sched._api_running:
            import uvicorn  # type: ignore

            print("Starting API at http://localhost:8000")
            Periodic_task_sched._api_running = True
            threading.Thread(
                target=uvicorn.run,
                args=(self.api_app,),
                kwargs={"host": "0.0.0.0", "port": 8000, "log_level": "info"},
                daemon=True,
            ).start()

    class PeriodicExecutor:
        """Handles the execution loop for a single periodic task."""

        def __init__(
            self,
            func: Callable,
            interval: int,
            priority: str,
            max_executions: Optional[int],
            dynamic_interval: bool,
            adaptive_priority: bool,
            dependent_task: Optional[str],
            enable_api: bool,
            database: Optional[DatabaseHandler],
        ) -> None:
            """Initialize the executor.

            Args:
                func: The task function to execute.
                interval: Execution interval in seconds.
                priority: Task priority level.
                max_executions: Maximum execution count.
                dynamic_interval: Allow dynamic interval adjustment.
                adaptive_priority: Allow adaptive priority.
                dependent_task: Dependent task name.
                enable_api: Whether task enables the API.
                database: Database handler instance.
            """
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

        def _save_task(self) -> None:
            """Persist task metadata to the database."""
            if self.database is None:
                return
            self.database.execute(
                "INSERT OR IGNORE INTO tasks "
                "(name, interval, priority, status, max_executions, "
                "current_executions, dynamic_interval, adaptive_priority, "
                "dependent_task, enable_api) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    self.func.__name__,
                    self.interval,
                    self.priority,
                    "stopped",
                    self.max_executions,
                    0,
                    self.dynamic_interval,
                    self.adaptive_priority,
                    self.dependent_task,
                    self.enable_api,
                ),
            )

        def start(self) -> None:
            """Start executing the task in a background thread."""
            if not self.running:
                self.running = True
                threading.Thread(target=self._run, daemon=True).start()

        def _run(self) -> None:
            """Main execution loop."""
            while self.running and self.execution_count < self.max_executions:
                if self.paused:
                    time.sleep(1)
                    continue

                if self.dependent_task and self.database:
                    result = self.database.fetch_all(
                        "SELECT status FROM tasks WHERE name = ?",
                        (self.dependent_task,),
                    )
                    if result and result[0][0] != "completed":
                        time.sleep(self.interval)
                        continue

                self.func()
                self.execution_count += 1

                if self.database:
                    self.database.execute(
                        "INSERT INTO logs "
                        "(timestamp, task_name, message) "
                        "VALUES (?, ?, ?)",
                        (
                            datetime.now().isoformat(),
                            self.func.__name__,
                            f"Executed {self.execution_count} times.",
                        ),
                    )
                    self.database.execute(
                        "UPDATE tasks SET status = 'completed' " "WHERE name = ?",
                        (self.func.__name__,),
                    )

                time.sleep(self.interval)

            self.running = False

        def stop(self) -> None:
            """Stop the task execution."""
            self.running = False

        def pause(self) -> None:
            """Pause the task execution."""
            self.paused = True

        def resume(self) -> None:
            """Resume the paused task."""
            self.paused = False
