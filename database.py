import os
import sqlite3
import hashlib
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).parent / "data" / "app.db"


def _get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                password_salt TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                weight REAL,
                height REAL,
                birth_date TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_surveys (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                age INTEGER,
                caffeine_per_day INTEGER,
                fast_food_per_week INTEGER,
                sleep_hours INTEGER,
                physical_activity_days INTEGER,
                screen_hours INTEGER,
                sleep_quality INTEGER,
                eat_after_10pm INTEGER,
                caffeine_after_8pm INTEGER,
                low_energy_frequency INTEGER,
                risk_score INTEGER,
                risk_level TEXT,
                projection_title TEXT,
                projection_status TEXT,
                projection_cluster TEXT,
                updated_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.commit()

    _ensure_user_column("age", "INTEGER")
    _ensure_survey_column("full_name", "TEXT")
    _ensure_survey_column("age", "INTEGER")
    _ensure_survey_column("risk_score", "INTEGER")
    _ensure_survey_column("risk_level", "TEXT")
    _ensure_survey_column("projection_title", "TEXT")
    _ensure_survey_column("projection_status", "TEXT")
    _ensure_survey_column("projection_cluster", "TEXT")


def _ensure_survey_column(column: str, col_type: str) -> None:
    with _get_conn() as conn:
        cols = conn.execute("PRAGMA table_info(user_surveys)").fetchall()
        existing = {row["name"] for row in cols}
        if column not in existing:
            conn.execute(f"ALTER TABLE user_surveys ADD COLUMN {column} {col_type}")
            conn.commit()


def _ensure_user_column(column: str, col_type: str) -> None:
    with _get_conn() as conn:
        cols = conn.execute("PRAGMA table_info(users)").fetchall()
        existing = {row["name"] for row in cols}
        if column not in existing:
            conn.execute(f"ALTER TABLE users ADD COLUMN {column} {col_type}")
            conn.commit()


def _hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    if salt is None:
        salt = os.urandom(16)
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return pwd_hash.hex(), salt.hex()


def create_user(
    name: str,
    email: str,
    password: str,
    gender: str | None = None,
    weight: float | None = None,
    height: float | None = None,
) -> int | None:
    password_hash, password_salt = _hash_password(password)
    safe_name = name.strip() if name else "User"
    with _get_conn() as conn:
        try:
            cur = conn.execute(
                """
                INSERT INTO users (name, email, password_hash, password_salt, gender, weight, height)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (safe_name, email.lower(), password_hash, password_salt, gender, weight, height),
            )
            conn.commit()
            return int(cur.lastrowid)
        except sqlite3.IntegrityError:
            return None


def get_user_by_email(email: str) -> dict[str, Any] | None:
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def verify_user(email: str, password: str) -> dict[str, Any] | None:
    user = get_user_by_email(email)
    if not user:
        return None
    salt = bytes.fromhex(user["password_salt"])
    pwd_hash, _ = _hash_password(password, salt)
    if pwd_hash == user["password_hash"]:
        return user
    return None


def update_user_profile(
    user_id: int,
    name: str,
    gender: str | None,
    weight: float | None,
    height: float | None,
    birth_date: str | None,
) -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            UPDATE users
            SET name = ?, gender = ?, weight = ?, height = ?, birth_date = ?
            WHERE id = ?
            """,
            (name, gender, weight, height, birth_date, user_id),
        )
        conn.commit()


def update_user_basic(user_id: int, name: str, age: int | None) -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            UPDATE users
            SET name = ?, age = ?
            WHERE id = ?
            """,
            (name, age, user_id),
        )
        conn.commit()


def update_user_metrics(
    user_id: int,
    gender: str | None = None,
    weight: float | None = None,
    height: float | None = None,
) -> None:
    fields: list[str] = []
    values: list[Any] = []

    if gender is not None:
        fields.append("gender = ?")
        values.append(gender)
    if weight is not None:
        fields.append("weight = ?")
        values.append(weight)
    if height is not None:
        fields.append("height = ?")
        values.append(height)

    if not fields:
        return

    values.append(user_id)
    with _get_conn() as conn:
        conn.execute(
            f"UPDATE users SET {', '.join(fields)} WHERE id = ?",
            values,
        )
        conn.commit()


def save_user_survey(user_id: int, data: dict[str, Any]) -> None:
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO user_surveys (
                user_id,
                full_name,
                age,
                caffeine_per_day,
                fast_food_per_week,
                sleep_hours,
                physical_activity_days,
                screen_hours,
                sleep_quality,
                eat_after_10pm,
                caffeine_after_8pm,
                low_energy_frequency,
                risk_score,
                risk_level,
                projection_title,
                projection_status,
                projection_cluster,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(user_id) DO UPDATE SET
                full_name = excluded.full_name,
                age = excluded.age,
                caffeine_per_day = excluded.caffeine_per_day,
                fast_food_per_week = excluded.fast_food_per_week,
                sleep_hours = excluded.sleep_hours,
                physical_activity_days = excluded.physical_activity_days,
                screen_hours = excluded.screen_hours,
                sleep_quality = excluded.sleep_quality,
                eat_after_10pm = excluded.eat_after_10pm,
                caffeine_after_8pm = excluded.caffeine_after_8pm,
                low_energy_frequency = excluded.low_energy_frequency,
                risk_score = excluded.risk_score,
                risk_level = excluded.risk_level,
                projection_title = excluded.projection_title,
                projection_status = excluded.projection_status,
                projection_cluster = excluded.projection_cluster,
                updated_at = datetime('now')
            """,
            (
                user_id,
                data.get("full_name"),
                data.get("age"),
                data.get("caffeine_per_day"),
                data.get("fast_food_per_week"),
                data.get("sleep_hours"),
                data.get("physical_activity_days"),
                data.get("screen_hours"),
                data.get("sleep_quality"),
                data.get("eat_after_10pm"),
                data.get("caffeine_after_8pm"),
                data.get("low_energy_frequency"),
                data.get("risk_score"),
                data.get("risk_level"),
                data.get("projection_title"),
                data.get("projection_status"),
                data.get("projection_cluster"),
            ),
        )
        conn.commit()


def get_user_survey(user_id: int) -> dict[str, Any] | None:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM user_surveys WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        return dict(row) if row else None


def update_user_projection(
    user_id: int,
    risk_score: int | None = None,
    risk_level: str | None = None,
    projection_title: str | None = None,
    projection_status: str | None = None,
    projection_cluster: str | None = None,
) -> None:
    fields: list[str] = []
    values: list[Any] = []

    if risk_score is not None:
        fields.append("risk_score = ?")
        values.append(risk_score)
    if risk_level is not None:
        fields.append("risk_level = ?")
        values.append(risk_level)
    if projection_title is not None:
        fields.append("projection_title = ?")
        values.append(projection_title)
    if projection_status is not None:
        fields.append("projection_status = ?")
        values.append(projection_status)
    if projection_cluster is not None:
        fields.append("projection_cluster = ?")
        values.append(projection_cluster)

    if not fields:
        return

    values.append(user_id)
    with _get_conn() as conn:
        conn.execute(
            f"UPDATE user_surveys SET {', '.join(fields)} WHERE user_id = ?",
            values,
        )
        conn.commit()
