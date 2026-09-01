"""Periodic task scheduler with FastAPI dashboard and database persistence."""

import asyncio
import concurrent.futures
import json
import socket
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

SECRET_KEY = "mysecretkeymustbeatleast32byteslong!"
ALGORITHM = "HS256"
DB_FILE = "task_logs_v14.db"


def _parse_cron_field(field_str: str, min_val: int, max_val: int) -> Set[int]:
    """Parse a single cron field into a set of matching integers."""
    result: Set[int] = set()
    for part in field_str.split(","):
        part = part.strip()
        if part == "*":
            result.update(range(min_val, max_val + 1))
        elif part.startswith("*/"):
            step = int(part[2:])
            result.update(range(min_val, max_val + 1, step))
        elif "-" in part:
            start_s, end_s = part.split("-")
            result.update(range(int(start_s), int(end_s) + 1))
        else:
            result.add(int(part))
    return result


def _get_seconds_to_next_cron(cron_str: str) -> float:
    """Calculate seconds remaining until next matching time for a 5-field cron string.

    Args:
        cron_str: 5-field cron string (e.g. '0 4,10,16,23 * * *' or '*/5 * * * *').

    Returns:
        Seconds to wait until the next matching minute.
    """
    fields = cron_str.strip().split()
    if len(fields) != 5:
        return 60.0

    minutes = _parse_cron_field(fields[0], 0, 59)
    hours = _parse_cron_field(fields[1], 0, 23)
    doms = _parse_cron_field(fields[2], 1, 31)
    months = _parse_cron_field(fields[3], 1, 12)
    dows = _parse_cron_field(fields[4], 0, 6)

    now = datetime.now()
    target = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
    limit = now + timedelta(days=366)

    while target < limit:
        if (
            target.minute in minutes
            and target.hour in hours
            and target.day in doms
            and target.month in months
            and target.weekday() in dows
        ):
            return max((target - now).total_seconds(), 0.1)
        target += timedelta(minutes=1)

    return 60.0


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
    """Periodic task scheduler with decorator-based registration and optional API.

    Usage:
        .. code-block:: python

            controller = Periodic_task_sched()
            controller.set_database()

            @controller.periodic_execution(interval=5)
            def my_task():
                print("Running...")

            my_task()
            controller.start_api()
    """

    _api_running = False

    def __init__(
        self,
        auto_database: bool = False,
        handle_signals: bool = False,
        db_config_json: Optional[str] = None,
        max_workers: Optional[int] = None,
    ) -> None:
        """Initialize the scheduler.

        Args:
            auto_database: Automatically configure database handler on init.
            handle_signals: Automatically register SIGINT and SIGTERM handlers.
            db_config_json: Optional JSON string with database connection configuration.
            max_workers: Maximum worker threads for execution pool.
        """
        self.database: Optional[DatabaseHandler] = None
        self.executors: Dict[str, "Periodic_task_sched.PeriodicExecutor"] = {}
        self.api_enabled = False
        self.api_app = None
        self.max_workers = max_workers

        if max_workers:
            self.thread_pool: Optional[concurrent.futures.ThreadPoolExecutor] = (
                concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
            )
        else:
            self.thread_pool = None

        if auto_database:
            self.set_database(db_config_json)

        if handle_signals:
            self._register_signals()

    def _register_signals(self) -> None:
        """Register SIGINT and SIGTERM signal handlers for graceful shutdown."""
        import signal

        def _signal_handler(signum: Any, frame: Any) -> None:
            print("\n[Scheduler] Interrupt signal received, stopping all tasks...")
            self.stop_all()

        try:
            signal.signal(signal.SIGINT, _signal_handler)
            signal.signal(signal.SIGTERM, _signal_handler)
        except (ValueError, TypeError):
            # Signal registration can fail if not in main thread
            pass

    def stop_all(self) -> None:
        """Stop all active task executors."""
        for executor in list(self.executors.values()):
            executor.stop()
        if self.thread_pool:
            self.thread_pool.shutdown(wait=False)

    def run_forever(self, poll_interval: float = 1.0) -> None:
        """Safely block main thread and handle graceful shutdown on interrupt."""
        self._register_signals()
        print("[Scheduler] Running tasks. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(poll_interval)
        except (KeyboardInterrupt, SystemExit):
            print("\n[Scheduler] Stopping all tasks...")
            self.stop_all()

    def _build_api_app(self):
        """Lazily build the FastAPI application with dashboard routes."""
        try:
            import jwt  # type: ignore
            import uvicorn  # type: ignore
            from fastapi import FastAPI, Form, HTTPException, Request
            from fastapi.responses import HTMLResponse, PlainTextResponse
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
                request=request,
                name="dashboard.html",
                context={"tasks": tasks, "logs": logs},
            )

        @self.api_app.get("/metrics")
        def metrics():
            lines = [
                "# HELP scheduler_tasks_total Total number of registered tasks.",
                "# TYPE scheduler_tasks_total gauge",
                f"scheduler_tasks_total {len(self.executors)}",
                "# HELP scheduler_task_executions_total Total executions per task.",
                "# TYPE scheduler_task_executions_total counter",
                "# HELP scheduler_task_failures_total Total failures per task.",
                "# TYPE scheduler_task_failures_total counter",
                "# HELP scheduler_task_duration_seconds Last execution duration per task.",
                "# TYPE scheduler_task_duration_seconds gauge",
            ]
            for name, ex in self.executors.items():
                lines.append(
                    f'scheduler_task_executions_total{{task="{name}"}} {ex.execution_count}'
                )
                lines.append(
                    f'scheduler_task_failures_total{{task="{name}"}} {ex.failure_count}'
                )
                lines.append(
                    f'scheduler_task_duration_seconds{{task="{name}"}} {ex.last_duration:.6f}'
                )
            return PlainTextResponse("\n".join(lines) + "\n")

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
            return self.templates.TemplateResponse(
                request=request, name="login.html", context={}
            )

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
        interval: Optional[int] = None,
        run_at: Optional[Union[str, List[str]]] = None,
        cron: Optional[str] = None,
        priority: str = "medium",
        max_executions: Optional[int] = None,
        dynamic_interval: bool = False,
        adaptive_priority: bool = False,
        dependent_task: Optional[str] = None,
        allow_concurrent: bool = True,
        on_success: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        enable_api: bool = False,
    ):
        """Register a function as a periodic task via decorator.

        Args:
            interval: Execution interval in seconds.
            run_at: Specific time(s) of day in 'HH:MM' format.
            cron: 5-field cron expression string (e.g. '0 4,10,16,23 * * *').
            priority: Task priority ('low', 'medium', 'high').
            max_executions: Max executions (None = unlimited).
            dynamic_interval: Allow dynamic interval adjustment.
            adaptive_priority: Allow adaptive priority.
            dependent_task: Name of task this one depends on.
            allow_concurrent: Allow overlapping executions if task takes longer than interval.
            on_success: Optional callback triggered on successful execution.
            on_error: Optional callback triggered when task raises an exception.
            enable_api: Enable the API dashboard for this task.

        Returns:
            Decorator that wraps the task function.

        Raises:
            ValueError: If neither interval, run_at, nor cron is provided.
        """
        if interval is None and run_at is None and cron is None:
            raise ValueError("Either 'interval', 'run_at', or 'cron' must be provided.")

        if enable_api:
            self.api_enabled = True

        def decorator(func: Callable) -> Callable:
            executor = self.PeriodicExecutor(
                func=func,
                interval=interval,
                run_at=run_at,
                cron=cron,
                priority=priority,
                max_executions=max_executions,
                dynamic_interval=dynamic_interval,
                adaptive_priority=adaptive_priority,
                dependent_task=dependent_task,
                allow_concurrent=allow_concurrent,
                on_success=on_success,
                on_error=on_error,
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
            interval: Optional[int] = None,
            priority: str = "medium",
            max_executions: Optional[int] = None,
            dynamic_interval: bool = False,
            adaptive_priority: bool = False,
            dependent_task: Optional[str] = None,
            enable_api: bool = False,
            database: Optional[DatabaseHandler] = None,
            run_at: Optional[Union[str, List[str]]] = None,
            cron: Optional[str] = None,
            allow_concurrent: bool = True,
            on_success: Optional[Callable[[Any], None]] = None,
            on_error: Optional[Callable[[Exception], None]] = None,
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
                run_at: Specific time(s) of day in 'HH:MM' format.
                cron: 5-field cron string.
                allow_concurrent: Allow concurrent/overlapping execution.
                on_success: Callback on success.
                on_error: Callback on error.
            """
            self.func = func
            self.interval = interval

            if isinstance(run_at, str):
                self.run_at: Optional[List[str]] = [run_at]
            elif isinstance(run_at, list):
                self.run_at = run_at
            else:
                self.run_at = None

            self.cron = cron
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
            self.allow_concurrent = allow_concurrent
            self.on_success = on_success
            self.on_error = on_error
            self.is_executing = False
            self.failure_count = 0
            self.last_duration = 0.0

            self._save_task()

        def _save_task(self) -> None:
            """Persist task metadata to the database."""
            if self.database is None:
                return
            interval_str = (
                str(self.interval)
                if self.interval
                else f"cron:{self.cron}" if self.cron else f"run_at:{self.run_at}"
            )
            self.database.execute(
                "INSERT OR IGNORE INTO tasks "
                "(name, interval, priority, status, max_executions, "
                "current_executions, dynamic_interval, adaptive_priority, "
                "dependent_task, enable_api) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    self.func.__name__,
                    interval_str,
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

        def _get_seconds_to_next_run_at(self) -> float:
            """Calculate seconds remaining until the next scheduled time in run_at.

            Returns:
                Seconds to wait until the next scheduled time.
            """
            if not self.run_at:
                return float(self.interval or 0)

            now = datetime.now()
            next_target: Optional[datetime] = None

            for t_str in self.run_at:
                try:
                    target_time = datetime.strptime(t_str.strip(), "%H:%M").time()
                except ValueError:
                    continue

                target_dt = datetime.combine(now.date(), target_time)
                if target_dt <= now:
                    target_dt += timedelta(days=1)

                if next_target is None or target_dt < next_target:
                    next_target = target_dt

            if next_target is None:
                return float(self.interval or 60)

            return max((next_target - now).total_seconds(), 0.1)

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
                        time.sleep(self.interval or 1)
                        continue

                if self.cron:
                    sleep_time = _get_seconds_to_next_cron(self.cron)
                    end_time = time.time() + sleep_time
                    while self.running and time.time() < end_time:
                        if self.paused:
                            break
                        time.sleep(min(1.0, end_time - time.time()))

                    if not self.running or self.paused:
                        continue
                elif self.run_at:
                    sleep_time = self._get_seconds_to_next_run_at()
                    end_time = time.time() + sleep_time
                    while self.running and time.time() < end_time:
                        if self.paused:
                            break
                        time.sleep(min(1.0, end_time - time.time()))

                    if not self.running or self.paused:
                        continue

                if not self.allow_concurrent and self.is_executing:
                    print(
                        f"[Task: {self.func.__name__}] Execution skipped: previous run still active."
                    )
                    if self.interval:
                        time.sleep(self.interval)
                    continue

                self.is_executing = True
                start_time = time.perf_counter()

                try:
                    if asyncio.iscoroutinefunction(self.func):
                        exec_result = asyncio.run(self.func())
                    else:
                        exec_result = self.func()

                    self.last_duration = time.perf_counter() - start_time
                    if self.on_success:
                        try:
                            self.on_success(exec_result)
                        except Exception as cb_err:
                            print(
                                f"[Task: {self.func.__name__}] on_success error: {cb_err}"
                            )
                except Exception as exc:
                    self.failure_count += 1
                    self.last_duration = time.perf_counter() - start_time
                    if self.on_error:
                        try:
                            self.on_error(exc)
                        except Exception as cb_err:
                            print(
                                f"[Task: {self.func.__name__}] on_error error: {cb_err}"
                            )
                finally:
                    self.is_executing = False

                self.execution_count += 1

                if self.database:
                    self.database.execute(
                        "INSERT INTO logs (timestamp, task_name, message) VALUES (?, ?, ?)",
                        (
                            datetime.now().isoformat(),
                            self.func.__name__,
                            f"Executed {self.execution_count} times.",
                        ),
                    )
                    self.database.execute(
                        "UPDATE tasks SET status = 'completed' WHERE name = ?",
                        (self.func.__name__,),
                    )

                if not self.run_at and not self.cron:
                    time.sleep(self.interval or 1)

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
