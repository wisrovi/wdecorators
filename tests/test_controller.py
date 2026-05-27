"""Tests for Periodic_task_sched controller (controller.py)."""

import json
import sqlite3
import threading
from datetime import datetime
from unittest.mock import MagicMock, PropertyMock, patch, call, ANY

import pytest


# ── Helpers ────────────────────────────────────────────────────────────


def _patch_db_file(tmp_path, monkeypatch):
    """Point DB_FILE to a temp path so tests don't clobber each other."""
    db_file = tmp_path / "test.db"
    monkeypatch.setattr(
        "wdecorators.periodic_scheduller.controller.DB_FILE", str(db_file)
    )
    return db_file


# ── Fixtures ───────────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _cleanup_api_flag():
    """Reset the class-level _api_running flag after each test."""
    yield
    from wdecorators.periodic_scheduller.controller import Periodic_task_sched

    Periodic_task_sched._api_running = False


@pytest.fixture
def ctrl():
    """A bare Periodic_task_sched instance with no database."""
    from wdecorators.periodic_scheduller.controller import Periodic_task_sched

    return Periodic_task_sched()


@pytest.fixture
def ctrl_with_db(tmp_path, monkeypatch):
    """Periodic_task_sched with a temporary SQLite database."""
    _patch_db_file(tmp_path, monkeypatch)
    from wdecorators.periodic_scheduller.controller import Periodic_task_sched

    controller = Periodic_task_sched()
    controller.set_database()
    return controller


# ═══════════════════════════════════════════════════════════════════════
#  DatabaseHandler
# ═══════════════════════════════════════════════════════════════════════


class TestDatabaseHandler:
    def test_init_sqlite(self, tmp_path, monkeypatch):
        _patch_db_file(tmp_path, monkeypatch)
        from wdecorators.periodic_scheduller.controller import DatabaseHandler

        db = DatabaseHandler()
        assert db.use_postgres is False
        assert isinstance(db.conn, sqlite3.Connection)

        tables = db.fetch_all("SELECT name FROM sqlite_master WHERE type='table'")
        names = {t[0] for t in tables}
        assert "logs" in names
        assert "tasks" in names
        db.conn.close()

    def test_init_postgres_fallback(self, tmp_path, monkeypatch):
        """Fall back to SQLite when psycopg2 is unavailable."""
        _patch_db_file(tmp_path, monkeypatch)

        real_import = __builtins__["__import__"]

        def mock_import(name, *args, **kwargs):
            if name == "psycopg2":
                raise ImportError("psycopg2 not installed")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr("builtins.__import__", mock_import)

        from wdecorators.periodic_scheduller.controller import DatabaseHandler

        db = DatabaseHandler(db_config={"host": "localhost"})
        assert db.use_postgres is False
        assert isinstance(db.conn, sqlite3.Connection)
        db.conn.close()

    def test_init_postgres_raises_on_connect(self, tmp_path, monkeypatch):
        """Fall back to SQLite when psycopg2 is available but connect fails."""
        _patch_db_file(tmp_path, monkeypatch)

        import psycopg2

        with patch.object(psycopg2, "connect", side_effect=Exception("conn refused")):
            from wdecorators.periodic_scheduller.controller import DatabaseHandler

            db = DatabaseHandler(db_config={"host": "localhost"})
            assert db.use_postgres is False
            assert isinstance(db.conn, sqlite3.Connection)
            db.conn.close()

    def test_init_postgres_success(self, tmp_path, monkeypatch):
        """PostgreSQL connection succeeds – uses psycopg2."""
        _patch_db_file(tmp_path, monkeypatch)

        import psycopg2

        mock_conn = MagicMock()
        with patch.object(psycopg2, "connect", return_value=mock_conn):
            from wdecorators.periodic_scheduller.controller import DatabaseHandler

            db = DatabaseHandler(db_config={"host": "pg.example.com"})
            assert db.use_postgres is True
            assert db.conn is mock_conn
            # _setup_database would have been called on the mock
            mock_conn.cursor.return_value.execute.assert_called()
            mock_conn.commit.assert_called()
            db.conn.close()

    def test_execute_and_fetch(self, tmp_path, monkeypatch):
        _patch_db_file(tmp_path, monkeypatch)
        from wdecorators.periodic_scheduller.controller import DatabaseHandler

        db = DatabaseHandler()
        db.execute(
            "INSERT INTO logs (timestamp, task_name, message) VALUES (?, ?, ?)",
            ("2024-01-01", "task_a", "hello"),
        )
        rows = db.fetch_all("SELECT * FROM logs")
        assert len(rows) == 1
        assert rows[0][1] == "2024-01-01"
        assert rows[0][2] == "task_a"
        assert rows[0][3] == "hello"

        # fetch_all with params
        rows2 = db.fetch_all(
            "SELECT * FROM logs WHERE task_name = ?", ("task_a",)
        )
        assert len(rows2) == 1

        # fetch_all with no results
        rows3 = db.fetch_all(
            "SELECT * FROM logs WHERE task_name = ?", ("nonexistent",)
        )
        assert rows3 == []

        # multiple rows
        db.execute(
            "INSERT INTO logs (timestamp, task_name, message) VALUES (?, ?, ?)",
            ("2024-01-02", "task_b", "world"),
        )
        rows4 = db.fetch_all("SELECT * FROM logs ORDER BY timestamp")
        assert len(rows4) == 2
        db.conn.close()

    def test_execute_sql_injection_safe(self, tmp_path, monkeypatch):
        """Ensure parameterised queries work safely."""
        _patch_db_file(tmp_path, monkeypatch)
        from wdecorators.periodic_scheduller.controller import DatabaseHandler

        db = DatabaseHandler()
        db.execute(
            "INSERT INTO logs (timestamp, task_name, message) VALUES (?, ?, ?)",
            ("ts", "safe_name", "safe_message"),
        )
        rows = db.fetch_all("SELECT * FROM logs")
        assert len(rows) == 1
        assert rows[0][2] == "safe_name"
        db.conn.close()

    def test_database_lock_type(self, tmp_path, monkeypatch):
        """Verify the lock is a threading.Lock."""
        _patch_db_file(tmp_path, monkeypatch)
        from wdecorators.periodic_scheduller.controller import DatabaseHandler

        db = DatabaseHandler()
        assert isinstance(db.lock, type(threading.Lock()))
        db.conn.close()


# ═══════════════════════════════════════════════════════════════════════
#  Periodic_task_sched  –  basic setup
# ═══════════════════════════════════════════════════════════════════════


class TestPeriodicTaskSchedSetup:
    def test_init(self, ctrl):
        assert ctrl.database is None
        assert ctrl.executors == {}
        assert ctrl.api_enabled is False
        assert ctrl.api_app is None

    def test_set_database_default(self, ctrl, tmp_path, monkeypatch):
        _patch_db_file(tmp_path, monkeypatch)
        ctrl.set_database()
        assert ctrl.database is not None
        assert isinstance(ctrl.database.conn, sqlite3.Connection)
        ctrl.database.conn.close()

    def test_set_database_with_json(self, ctrl, tmp_path, monkeypatch):
        _patch_db_file(tmp_path, monkeypatch)

        real_import = __builtins__["__import__"]

        def mock_import(name, *args, **kwargs):
            if name == "psycopg2":
                raise ImportError("no psycopg2")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr("builtins.__import__", mock_import)

        config = json.dumps({"host": "db.example.com", "port": 5432})
        ctrl.set_database(config)
        assert ctrl.database is not None
        assert ctrl.database.use_postgres is False
        ctrl.database.conn.close()

    def test_set_database_with_none_json(self, ctrl, tmp_path, monkeypatch):
        _patch_db_file(tmp_path, monkeypatch)
        ctrl.set_database(None)
        assert ctrl.database is not None
        ctrl.database.conn.close()

    def test_set_database_empty_string_json(self, ctrl, tmp_path, monkeypatch):
        _patch_db_file(tmp_path, monkeypatch)
        ctrl.set_database("")
        assert ctrl.database is not None
        ctrl.database.conn.close()


# ═══════════════════════════════════════════════════════════════════════
#  Periodic_task_sched  –  task registration
# ═══════════════════════════════════════════════════════════════════════


class TestTaskRegistration:
    def test_registers_basic(self, ctrl_with_db):
        ctrl = ctrl_with_db

        @ctrl.periodic_execution(interval=5)
        def my_task():
            pass

        assert "my_task" in ctrl.executors
        ex = ctrl.executors["my_task"]
        assert ex.interval == 5
        assert ex.priority == "medium"
        assert ex.max_executions == float("inf")
        assert ex.database is not None
        assert ex.dependent_task is None
        assert ex.dynamic_interval is False
        assert ex.adaptive_priority is False
        assert ex.enable_api is False

    def test_all_parameters(self, ctrl_with_db):
        ctrl = ctrl_with_db

        @ctrl.periodic_execution(
            interval=10,
            priority="high",
            max_executions=5,
            dynamic_interval=True,
            adaptive_priority=True,
            dependent_task="other",
            enable_api=True,
        )
        def full_task():
            pass

        assert ctrl.api_enabled is True
        ex = ctrl.executors["full_task"]
        assert ex.interval == 10
        assert ex.priority == "high"
        assert ex.max_executions == 5
        assert ex.dynamic_interval is True
        assert ex.adaptive_priority is True
        assert ex.dependent_task == "other"
        assert ex.enable_api is True

    def test_max_executions_none_defaults_inf(self, ctrl_with_db):
        ctrl = ctrl_with_db

        @ctrl.periodic_execution(interval=1, max_executions=None)
        def inf_task():
            pass

        assert inf_task().max_executions == float("inf")

    def test_without_database(self, ctrl):
        @ctrl.periodic_execution(interval=5)
        def no_db_task():
            pass

        assert "no_db_task" in ctrl.executors
        assert ctrl.executors["no_db_task"].database is None

        # _save_task should not raise
        ctrl.executors["no_db_task"]._save_task()

    def test_wrapper_starts_executor(self, ctrl_with_db):
        ctrl = ctrl_with_db

        @ctrl.periodic_execution(interval=5)
        def starter():
            pass

        with patch.object(ctrl.executors["starter"], "start") as mock_start:
            result = starter()
            mock_start.assert_called_once()
            assert result is ctrl.executors["starter"]

    def test_multiple_tasks(self, ctrl_with_db):
        ctrl = ctrl_with_db

        @ctrl.periodic_execution(interval=1)
        def task_a():
            pass

        @ctrl.periodic_execution(interval=2)
        def task_b():
            pass

        assert set(ctrl.executors.keys()) == {"task_a", "task_b"}


# ═══════════════════════════════════════════════════════════════════════
#  Periodic_task_sched  –  is_port_in_use / start_api
# ═══════════════════════════════════════════════════════════════════════


class TestNetworkingAndApi:
    def test_is_port_in_use_false(self, ctrl):
        with patch(
            "wdecorators.periodic_scheduller.controller.socket.socket"
        ) as mock_sock:
            inst = mock_sock.return_value.__enter__.return_value
            inst.connect_ex.return_value = 1  # not in use
            assert ctrl.is_port_in_use(8000) is False

    def test_is_port_in_use_true(self, ctrl):
        with patch(
            "wdecorators.periodic_scheduller.controller.socket.socket"
        ) as mock_sock:
            inst = mock_sock.return_value.__enter__.return_value
            inst.connect_ex.return_value = 0  # in use
            assert ctrl.is_port_in_use(8000) is True

    def test_start_api_not_enabled(self, ctrl, capsys):
        ctrl.start_api()
        out, _ = capsys.readouterr()
        assert "API not enabled" in out

    def test_start_api_port_in_use(self, ctrl, capsys):
        ctrl.api_enabled = True
        with patch.object(ctrl, "is_port_in_use", return_value=True):
            ctrl.start_api()
        out, _ = capsys.readouterr()
        assert "already running" in out

    def test_start_api_success(self, ctrl, capsys):
        ctrl.api_enabled = True
        with (
            patch.object(ctrl, "is_port_in_use", return_value=False),
            patch.object(ctrl, "_build_api_app") as mock_build,
            patch(
                "wdecorators.periodic_scheduller.controller.threading.Thread"
            ) as mock_thread,
        ):
            ctrl.start_api()

        out, _ = capsys.readouterr()
        assert "Starting API" in out
        mock_build.assert_called_once()
        mock_thread.assert_called_once()
        args, kwargs = mock_thread.call_args
        assert kwargs["target"] is not None
        assert kwargs["args"] == (ctrl.api_app,)
        assert kwargs["kwargs"] == {"host": "0.0.0.0", "port": 8000, "log_level": "info"}
        assert kwargs["daemon"] is True
        # The mock thread's start() should have been called
        mock_thread.return_value.start.assert_called_once()

    def test_start_api_twice(self, ctrl, capsys):
        """Second call should be a no-op because _api_running is True."""
        ctrl.api_enabled = True
        with (
            patch.object(ctrl, "is_port_in_use", return_value=False),
            patch.object(ctrl, "_build_api_app"),
            patch("uvicorn.run"),
            patch("wdecorators.periodic_scheduller.controller.threading.Thread"),
        ):
            ctrl.start_api()
            capsys.readouterr()  # discard first output
            ctrl.start_api()

        out, _ = capsys.readouterr()
        assert out == ""

    def test_verify_admin_valid(self, ctrl):
        import jwt
        token = jwt.encode({"role": "admin"}, SECRET_KEY, algorithm="HS256")
        token = jwt.encode({"role": "supervisor"}, SECRET_KEY, algorithm="HS256")
        token = jwt.encode({"role": "user"}, SECRET_KEY, algorithm="HS256")
        with pytest.raises(Exception):
            ctrl.verify_admin(token)

    def test_verify_admin_invalid_token(self, ctrl):
        with pytest.raises(Exception):
            ctrl.verify_admin("not.a.valid.token")

    def test_verify_admin_import_error(self, ctrl):
        """Simulate missing jwt dependency."""
        real_import = __builtins__["__import__"]

        def mock_import(name, *args, **kwargs):
            if name in ("jwt", "jwt."):
                raise ImportError("no jwt")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            with pytest.raises(ImportError, match="verify_admin requires"):
                ctrl.verify_admin("some.token")


# ═══════════════════════════════════════════════════════════════════════
#  Periodic_task_sched  –  FastAPI dashboard (via TestClient)
# ═══════════════════════════════════════════════════════════════════════


class TestFastApiEndpoints:
    """Requires fastapi + uvicorn + jinja2 + python-multipart + pyjwt."""

    def _make_client(self, ctrl):
        """Build the FastAPI app and return a TestClient."""
        ctrl._build_api_app()
        from starlette.testclient import TestClient

        return TestClient(ctrl.api_app)

    def test_dashboard(self, ctrl_with_db, tmp_path, monkeypatch):
        _patch_db_file(tmp_path, monkeypatch)
        ctrl = ctrl_with_db
        client = self._make_client(ctrl)
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]

    def test_dashboard_with_logs(self, ctrl_with_db, tmp_path, monkeypatch):
        _patch_db_file(tmp_path, monkeypatch)
        ctrl = ctrl_with_db
        # Insert a log entry
        ctrl.database.execute(
            "INSERT INTO logs (timestamp, task_name, message) VALUES (?, ?, ?)",
            ("2024-06-01T12:00:00", "test_task", "ran 1x"),
        )
        client = self._make_client(ctrl)
        resp = client.get("/")
        assert resp.status_code == 200

    def test_login_page(self, ctrl):
        client = self._make_client(ctrl)
        resp = client.get("/login")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]

    def test_login_admin(self, ctrl):
        client = self._make_client(ctrl)
        resp = client.post("/login", data={"username": "admin", "password": "admin"})
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        import jwt

        payload = jwt.decode(data["token"], SECRET_KEY, algorithms=["HS256"])
        assert payload["role"] == "admin"

    def test_login_supervisor(self, ctrl):
        client = self._make_client(ctrl)
        resp = client.post(
            "/login", data={"username": "user", "password": "pass"}
        )
        assert resp.status_code == 200
        data = resp.json()
        import jwt

        payload = jwt.decode(data["token"], SECRET_KEY, algorithms=["HS256"])
        assert payload["role"] == "supervisor"

    def test_list_tasks(self, ctrl):
        ctrl.api_enabled = True

        @ctrl.periodic_execution(interval=5)
        def alpha():
            pass

        @ctrl.periodic_execution(interval=10)
        def beta():
            pass

        import jwt

        token = jwt.encode({"role": "admin"}, SECRET_KEY, algorithm="HS256")
        client = self._make_client(ctrl)
        resp = client.post("/list_tasks/", data={"token": token})
        assert resp.status_code == 200
        assert set(resp.json()) == {"alpha", "beta"}

    def test_pause_and_resume_task(self, ctrl):
        ctrl.api_enabled = True

        @ctrl.periodic_execution(interval=5)
        def my_task():
            pass

        import jwt

        token = jwt.encode({"role": "admin"}, SECRET_KEY, algorithm="HS256")
        client = self._make_client(ctrl)

        # pause
        resp = client.post("/pause_task/", data={"task_name": "my_task", "token": token})
        assert resp.status_code == 200
        assert resp.json() == {"status": "Task 'my_task' paused."}
        assert ctrl.executors["my_task"].paused is True

        # resume
        resp = client.post(
            "/resume_task/", data={"task_name": "my_task", "token": token}
        )
        assert resp.status_code == 200
        assert resp.json() == {"status": "Task 'my_task' resumed."}
        assert ctrl.executors["my_task"].paused is False

    def test_stop_task(self, ctrl):
        ctrl.api_enabled = True

        @ctrl.periodic_execution(interval=5)
        def my_task():
            pass

        import jwt

        token = jwt.encode({"role": "admin"}, SECRET_KEY, algorithm="HS256")
        client = self._make_client(ctrl)

        resp = client.post("/stop_task/", data={"task_name": "my_task", "token": token})
        assert resp.status_code == 200
        assert resp.json() == {"status": "Task 'my_task' stopped."}
        assert ctrl.executors["my_task"].running is False

    def test_pause_task_not_found(self, ctrl):
        ctrl.api_enabled = True
        import jwt

        token = jwt.encode({"role": "admin"}, SECRET_KEY, algorithm="HS256")
        client = self._make_client(ctrl)

        resp = client.post(
            "/pause_task/", data={"task_name": "nope", "token": token}
        )
        assert resp.status_code == 200
        assert resp.json() == {"error": "Task 'nope' not found."}

    def test_stop_task_not_found(self, ctrl):
        ctrl.api_enabled = True
        import jwt

        token = jwt.encode({"role": "admin"}, SECRET_KEY, algorithm="HS256")
        client = self._make_client(ctrl)

        resp = client.post(
            "/stop_task/", data={"task_name": "nope", "token": token}
        )
        assert resp.status_code == 200
        assert resp.json() == {"error": "Task 'nope' not found."}

    def test_resume_task_not_found(self, ctrl):
        ctrl.api_enabled = True
        import jwt

        token = jwt.encode({"role": "admin"}, SECRET_KEY, algorithm="HS256")
        client = self._make_client(ctrl)

        resp = client.post(
            "/resume_task/", data={"task_name": "nope", "token": token}
        )
        assert resp.status_code == 200
        assert resp.json() == {"error": "Task 'nope' not found."}

    def test_execute_python_task_valid(self, ctrl, tmp_path, monkeypatch):
        _patch_db_file(tmp_path, monkeypatch)
        ctrl.set_database()
        ctrl.api_enabled = True
        import jwt

        token = jwt.encode({"role": "admin"}, SECRET_KEY, algorithm="HS256")
        client = self._make_client(ctrl)

        code = """
def task_function():
    pass
"""
        resp = client.post(
            "/execute_python_task/",
            data={
                "task_code": code,
                "interval": 3,
                "priority": "low",
                "token": token,
            },
        )
        assert resp.status_code == 200
        assert resp.json() == {"status": "New task created and running."}
        assert "task_function" in ctrl.executors
        ctrl.executors["task_function"].stop()

    def test_execute_python_task_missing_function(self, ctrl):
        ctrl.api_enabled = True
        import jwt

        token = jwt.encode({"role": "admin"}, SECRET_KEY, algorithm="HS256")
        client = self._make_client(ctrl)

        resp = client.post(
            "/execute_python_task/",
            data={
                "task_code": "x = 1",
                "interval": 3,
                "priority": "low",
                "token": token,
            },
        )
        assert resp.status_code == 200
        assert resp.json() == {"error": "'task_function' not found in provided code."}

    def test_execute_python_task_syntax_error(self, ctrl):
        ctrl.api_enabled = True
        import jwt

        token = jwt.encode({"role": "admin"}, SECRET_KEY, algorithm="HS256")
        client = self._make_client(ctrl)

        resp = client.post(
            "/execute_python_task/",
            data={
                "task_code": "invalid syntax {{{",
                "interval": 3,
                "priority": "low",
                "token": token,
            },
        )
        assert resp.status_code == 200
        assert "error" in resp.json()

    def test_build_api_app_import_error(self, ctrl):
        """Simulate missing dependencies."""
        real_import = __builtins__["__import__"]

        def mock_import(name, *args, **kwargs):
            if name in ("jwt",):
                raise ImportError("no jwt")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            with pytest.raises(ImportError, match="Periodic_task_sched API requires"):
                ctrl._build_api_app()


# ═══════════════════════════════════════════════════════════════════════
#  PeriodicExecutor
# ═══════════════════════════════════════════════════════════════════════


class TestPeriodicExecutorInit:
    def test_init_defaults(self, ctrl_with_db):
        ctrl = ctrl_with_db
        executor = ctrl.PeriodicExecutor(
            func=lambda: None,
            interval=5,
            priority="medium",
            max_executions=None,
            dynamic_interval=False,
            adaptive_priority=False,
            dependent_task=None,
            enable_api=False,
            database=ctrl.database,
        )
        assert executor.interval == 5
        assert executor.max_executions == float("inf")
        assert executor.execution_count == 0
        assert executor.running is False
        assert executor.paused is False
        assert executor.database is not None

    def test_init_without_database(self, ctrl):
        executor = ctrl.PeriodicExecutor(
            func=lambda: None,
            interval=5,
            priority="medium",
            max_executions=3,
            dynamic_interval=False,
            adaptive_priority=False,
            dependent_task=None,
            enable_api=False,
            database=None,
        )
        assert executor.max_executions == 3
        assert executor.database is None

    def test_save_task_persists(self, ctrl_with_db, tmp_path, monkeypatch):
        _patch_db_file(tmp_path, monkeypatch)
        ctrl = ctrl_with_db

        def dummy():
            pass

        executor = ctrl.PeriodicExecutor(
            func=dummy,
            interval=7,
            priority="low",
            max_executions=10,
            dynamic_interval=True,
            adaptive_priority=False,
            dependent_task="dep_name",
            enable_api=True,
            database=ctrl.database,
        )

        rows = ctrl.database.fetch_all("SELECT * FROM tasks WHERE name = ?", ("dummy",))
        assert len(rows) == 1
        assert rows[0][2] == 7  # interval
        assert rows[0][3] == "low"  # priority
        assert rows[0][5] == 10  # max_executions
        assert rows[0][6] == 0  # current_executions
        assert rows[0][7] == 1  # dynamic_interval
        assert rows[0][8] == 0  # adaptive_priority
        assert rows[0][9] == "dep_name"  # dependent_task
        assert rows[0][10] == 1  # enable_api

    def test_save_task_no_db(self, ctrl):
        executor = ctrl.PeriodicExecutor(
            func=lambda: None,
            interval=5,
            priority="medium",
            max_executions=None,
            dynamic_interval=False,
            adaptive_priority=False,
            dependent_task=None,
            enable_api=False,
            database=None,
        )
        # Should not raise
        executor._save_task()


class TestPeriodicExecutorLifecycle:
    def test_start_creates_thread(self, ctrl):
        executor = ctrl.PeriodicExecutor(
            func=lambda: None,
            interval=5,
            priority="medium",
            max_executions=1,
            dynamic_interval=False,
            adaptive_priority=False,
            dependent_task=None,
            enable_api=False,
            database=None,
        )

        with patch(
            "wdecorators.periodic_scheduller.controller.threading.Thread"
        ) as mock_thread:
            executor.start()
            mock_thread.assert_called_once_with(target=executor._run, daemon=True)
            mock_thread.return_value.start.assert_called_once()

    def test_start_already_running(self, ctrl):
        executor = ctrl.PeriodicExecutor(
            func=lambda: None,
            interval=5,
            priority="medium",
            max_executions=1,
            dynamic_interval=False,
            adaptive_priority=False,
            dependent_task=None,
            enable_api=False,
            database=None,
        )
        executor.running = True
        with patch(
            "wdecorators.periodic_scheduller.controller.threading.Thread"
        ) as mock_thread:
            executor.start()
            mock_thread.assert_not_called()

    def test_stop(self, ctrl):
        executor = ctrl.PeriodicExecutor(
            func=lambda: None,
            interval=5,
            priority="medium",
            max_executions=1,
            dynamic_interval=False,
            adaptive_priority=False,
            dependent_task=None,
            enable_api=False,
            database=None,
        )
        executor.running = True
        executor.stop()
        assert executor.running is False

    def test_pause_and_resume(self, ctrl):
        executor = ctrl.PeriodicExecutor(
            func=lambda: None,
            interval=5,
            priority="medium",
            max_executions=1,
            dynamic_interval=False,
            adaptive_priority=False,
            dependent_task=None,
            enable_api=False,
            database=None,
        )
        executor.pause()
        assert executor.paused is True
        executor.resume()
        assert executor.paused is False


class TestPeriodicExecutorRun:
    """Tests for _run() called directly with mocked time."""

    def test_run_completes_max_executions(self, ctrl):
        calls = []
        executor = ctrl.PeriodicExecutor(
            func=lambda: calls.append(1),
            interval=1,
            priority="medium",
            max_executions=3,
            dynamic_interval=False,
            adaptive_priority=False,
            dependent_task=None,
            enable_api=False,
            database=None,
        )
        executor.running = True

        with patch("wdecorators.periodic_scheduller.controller.time.sleep"):
            executor._run()

        assert len(calls) == 3
        assert executor.running is False
        assert executor.execution_count == 3

    def test_run_logs_to_database(self, ctrl_with_db, tmp_path, monkeypatch):
        _patch_db_file(tmp_path, monkeypatch)
        ctrl = ctrl_with_db

        calls = []
        executor = ctrl.PeriodicExecutor(
            func=lambda: calls.append(1),
            interval=1,
            priority="medium",
            max_executions=2,
            dynamic_interval=False,
            adaptive_priority=False,
            dependent_task=None,
            enable_api=False,
            database=ctrl.database,
        )
        executor.running = True

        with patch("wdecorators.periodic_scheduller.controller.time.sleep"):
            executor._run()

        assert len(calls) == 2

        # Check logs table
        logs = ctrl.database.fetch_all("SELECT * FROM logs ORDER BY id")
        assert len(logs) == 2
        assert logs[0][2] == "<lambda>"  # task_name
        assert logs[1][2] == "<lambda>"
        assert "Executed 1 times" in logs[0][3]
        assert "Executed 2 times" in logs[1][3]

        # Check tasks table status updated
        tasks = ctrl.database.fetch_all(
            "SELECT * FROM tasks WHERE name = ?", ("<lambda>",)
        )
        assert len(tasks) == 1
        assert tasks[0][4] == "completed"

    def test_run_pause_resume(self, ctrl):
        """Pausing should halt execution; resuming should continue."""
        execution_order = []

        def tracker():
            execution_order.append(len(execution_order) + 1)

        executor = ctrl.PeriodicExecutor(
            func=tracker,
            interval=1,
            priority="medium",
            max_executions=4,
            dynamic_interval=False,
            adaptive_priority=False,
            dependent_task=None,
            enable_api=False,
            database=None,
        )
        executor.running = True
        executor.paused = True  # start paused

        call_count = []

        def sleeper(secs):
            call_count.append(secs)
            # After 3 sleep cycles, unpause
            if len(call_count) == 3:
                executor.paused = False
            # After 4 executions, stop
            if executor.execution_count >= 4:
                executor.running = False

        with patch("wdecorators.periodic_scheduller.controller.time.sleep", sleeper):
            executor._run()

        assert len(execution_order) == 4

    def test_run_no_database(self, ctrl):
        """Without database, _run should execute but skip logging."""
        calls = []
        executor = ctrl.PeriodicExecutor(
            func=lambda: calls.append(1),
            interval=1,
            priority="medium",
            max_executions=2,
            dynamic_interval=False,
            adaptive_priority=False,
            dependent_task=None,
            enable_api=False,
            database=None,
        )
        executor.running = True

        with patch("wdecorators.periodic_scheduller.controller.time.sleep"):
            executor._run()

        assert len(calls) == 2
        assert executor.execution_count == 2

    def test_run_dependent_task_blocks(self, ctrl):
        """When dependent task is not completed, execution is skipped."""
        calls = []
        db = MagicMock()
        db.fetch_all.return_value = [("pending",)]

        executor = ctrl.PeriodicExecutor(
            func=lambda: calls.append(1),
            interval=1,
            priority="medium",
            max_executions=2,
            dynamic_interval=False,
            adaptive_priority=False,
            dependent_task="other",
            enable_api=False,
            database=db,
        )
        executor.running = True

        # First 2 calls to fetch_all return pending → blocks,
        # next 2 calls return completed → allows execution
        db.fetch_all.side_effect = [
            [("pending",)],
            [("pending",)],
            [("completed",)],
            [("completed",)],
        ]

        with patch("wdecorators.periodic_scheduller.controller.time.sleep"):
            executor._run()

        assert len(calls) == 2

    def test_run_dependent_task_not_in_db(self, ctrl):
        """When dependent task doesn't exist in DB, execution proceeds."""
        calls = []
        db = MagicMock()
        db.fetch_all.return_value = []  # empty result

        executor = ctrl.PeriodicExecutor(
            func=lambda: calls.append(1),
            interval=1,
            priority="medium",
            max_executions=2,
            dynamic_interval=False,
            adaptive_priority=False,
            dependent_task="nonexistent",
            enable_api=False,
            database=db,
        )
        executor.running = True

        with patch("wdecorators.periodic_scheduller.controller.time.sleep"):
            executor._run()

        assert len(calls) == 2

    def test_run_stop_midway(self, ctrl):
        """Calling stop() during execution terminates the loop."""
        calls = []

        def target():
            calls.append(1)

        executor = ctrl.PeriodicExecutor(
            func=target,
            interval=1,
            priority="medium",
            max_executions=10,
            dynamic_interval=False,
            adaptive_priority=False,
            dependent_task=None,
            enable_api=False,
            database=None,
        )
        executor.running = True

        def stop_after_one(secs):
            if executor.execution_count >= 1:
                executor.stop()

        with patch("wdecorators.periodic_scheduller.controller.time.sleep", stop_after_one):
            executor._run()

        assert len(calls) == 1
        assert executor.running is False

    def test_run_dependent_task_does_not_block_when_no_db(self, ctrl):
        """dependent_task is ignored when database is None."""
        calls = []
        executor = ctrl.PeriodicExecutor(
            func=lambda: calls.append(1),
            interval=1,
            priority="medium",
            max_executions=2,
            dynamic_interval=False,
            adaptive_priority=False,
            dependent_task="other",
            enable_api=False,
            database=None,
        )
        executor.running = True

        with patch("wdecorators.periodic_scheduller.controller.time.sleep"):
            executor._run()

        assert len(calls) == 2
