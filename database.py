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
                gender TEXT,
                weight REAL,
                height REAL,
                birth_date TEXT
            )
            """
        )
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
