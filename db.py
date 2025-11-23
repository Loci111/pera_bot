from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List, Optional

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Json


class Database:
    def __init__(self, dsn: Dict[str, Any], logger):
        self.logger = logger
        self.connection = psycopg.connect(**dsn, autocommit=True, row_factory=dict_row)
        self.logger.info("Подключение к базе данных установлено")
        self.create_tables()

    def create_tables(self) -> None:
        queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                last_activity TIMESTAMP DEFAULT NOW()
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                message_text TEXT,
                message_date TIMESTAMP DEFAULT NOW()
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS bot_events (
                id SERIAL PRIMARY KEY,
                event_type TEXT NOT NULL,
                event_data JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT NOW()
            );
            """,
        ]

        with self.connection.cursor() as cur:
            for query in queries:
                cur.execute(query)
        self.logger.info("Таблицы проверены и созданы при необходимости")

    def upsert_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> int:
        query = """
        INSERT INTO users (telegram_id, username, first_name, last_name, last_activity)
        VALUES (%s, %s, %s, %s, NOW())
        ON CONFLICT (telegram_id) DO UPDATE SET
            username = EXCLUDED.username,
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            last_activity = NOW()
        RETURNING id;
        """
        with self.connection.cursor() as cur:
            cur.execute(query, (telegram_id, username, first_name, last_name))
            user_id = cur.fetchone()["id"]
        return user_id

    def log_message(self, user_id: int, text: str, message_date: Optional[dt.datetime] = None) -> None:
        query = """
        INSERT INTO messages (user_id, message_text, message_date)
        VALUES (%s, %s, %s)
        """
        with self.connection.cursor() as cur:
            cur.execute(query, (user_id, text, message_date or dt.datetime.now()))

    def record_event(self, event_type: str, event_data: Optional[Dict[str, Any]] = None) -> None:
        query = """
        INSERT INTO bot_events (event_type, event_data)
        VALUES (%s, %s)
        """
        with self.connection.cursor() as cur:
            cur.execute(query, (event_type, Json(event_data or {})))

    def has_event_for_user(self, event_type: str, telegram_id: int) -> bool:
        query = """
        SELECT 1
        FROM bot_events
        WHERE event_type = %s AND event_data->>'telegram_id' = %s
        LIMIT 1;
        """
        with self.connection.cursor() as cur:
            cur.execute(query, (event_type, str(telegram_id)))
            return cur.fetchone() is not None

    def get_users_by_event(self, event_type: str) -> List[int]:
        query = """
        SELECT DISTINCT (event_data->>'telegram_id')::bigint AS telegram_id
        FROM bot_events
        WHERE event_type = %s
        ORDER BY telegram_id;
        """
        with self.connection.cursor() as cur:
            cur.execute(query, (event_type,))
            rows = cur.fetchall()
        return [row["telegram_id"] for row in rows if row.get("telegram_id") is not None]

    def get_all_users(self) -> List[Dict[str, Any]]:
        query = """
        SELECT telegram_id, username, first_name, last_name, created_at, last_activity
        FROM users
        ORDER BY created_at DESC;
        """
        with self.connection.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

    def count_unique_events(self, event_type: str) -> int:
        query = """
        SELECT COUNT(DISTINCT event_data->>'telegram_id') AS total
        FROM bot_events
        WHERE event_type = %s;
        """
        with self.connection.cursor() as cur:
            cur.execute(query, (event_type,))
            result = cur.fetchone()
        return int(result["total"]) if result else 0

    def close(self) -> None:
        self.connection.close()
        self.logger.info("Подключение к базе данных закрыто")

