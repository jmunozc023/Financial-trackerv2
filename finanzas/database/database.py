from __future__ import annotations

import sqlite3
import calendar
from pathlib import Path

from ..config import DB_PATH

class Database:
    def __init__(self, path: Path = DB_PATH): # Initialize the Database class with a default path to the database file
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.initialize()
    def initialize(self): # Create the transactions table if it doesn't exist
        self.conn.execute("""
        PRAGMA foreign_keys = ON;

        -- Create the statement_imports table if it doesn't exist
        CREATE TABLE IF NOT EXISTS statement_imports(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bank TEXT NOT NULL,
            statement_month TEXT NOT NULL,
            statement_year TEXT NOT NULL,
            source TEXT NOT NULL,
            imported_at TEXT DEFAULT CURRENT_TIMESTAMP);

        -- Create the statements table if it doesn't exist
        CREATE TABLE IF NOT EXISTS statements(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bank TEXT NOT NULL,
            card TEXT NOT NULL,
            last4_digits TEXT NOT NULL,
            loyalty_plan TEXT NOT NULL DEFAULT '',
            statement_month TEXT NOT NULL,
            statement_year TEXT NOT NULL,
            due_date TEXT,
            minimum_crc REAL NOT NULL DEFAULT 0,
            minimum_usd REAL NOT NULL DEFAULT 0,
            due_crc REAL NOT NULL DEFAULT 0,
            due_usd REAL NOT NULL DEFAULT 0,
            source TEXT,
            

            )
        """)