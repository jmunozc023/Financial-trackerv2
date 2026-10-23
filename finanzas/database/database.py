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
        self.conn.executescript("""
        PRAGMA foreign_keys = ON;

        -- Create the members table if it doesn't exist
        CREATE TABLE IF NOT EXISTS members(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        -- Create the statement_imports table if it doesn't exist
        CREATE TABLE IF NOT EXISTS statement_imports(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bank TEXT NOT NULL,
            statement_month TEXT NOT NULL,
            statement_year TEXT NOT NULL,
            source TEXT NOT NULL,
            imported_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

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
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            import_id INTEGER REFERENCES statement_imports(id) ON DELETE CASCADE,
            UNIQUE(bank,last4_digits,statement_month,statement_year,due_date)
        );

        -- Create the movements table if it doesn't exist
        CREATE TABLE IF NOT EXISTS movements(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL CHECK(type IN ('Ingreso', 'Egreso')),
            description TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('Despositos', 'Salario', 'Ahorro', 'Cuentas', 'Carro', 'Ropa', 'Servicios', 'Casa', 'Entretenimiento', 'Salud', 'Comida', 'Mascotas', 'Transporte', 'Otros')),
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'CRC',
            movement_date TEXT NOT NULL,
            member_id INTEGER REFERENCES members(id)
        );

        -- Create the recurring_movements table if it doesn't exist
        CREATE TABLE IF NOT EXISTS recurring_movements(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL CHECK(type IN ('Ingreso', 'Egreso')),
            description TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('Despositos', 'Salario', 'Ahorro', 'Cuentas', 'Carro', 'Ropa', 'Servicios', 'Casa', 'Entretenimiento', 'Salud', 'Comida', 'Mascotas', 'Transporte', 'Otros')),
            amount REAL NOT NULL,
            currency TEXT NOT NULL DEFAULT 'CRC',
            person_id INTEGER REFERENCES members(id),
            start_date TEXT NOT NULL,
            end_date TEXT,
            day_of_month INTEGER NOT NULL CHECK(day_of_month BETWEEN 1 AND 31),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        -- Create the rates table if it doesn't exist
        CREATE TABLE IF NOT EXISTS rates(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT NOT NULL,
            crc_to_usd REAL NOT NULL,
            source TEXT DEFAULT 'Manual'
        );

        -- Create the statement_transaction table if it doesn't exist
        CREATE TABLE IF NOT EXISTS statement_transaction(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            statement_id INTEGER NOT NULL REFERENCES statements(id) ON DELETE CASCADE,
            transaction_date TEXT NOT NULL,
            description TEXT NOT NULL,
            place TEXT DEFAULT '',
            amount REAL NOT NULL,
            currency TEXT NOT NULL CHECK(currency IN ('CRC', 'USD')),
            source_card_last4 TEXT NOT NULL,
            source_card_holder TEXT DEFAULT '',
            assigned_to_id INTEGER REFERENCES members(id)
        );

        -- Create the period_notes table if it doesn't exist
        CREATE TABLE IF NOT EXISTS period_notes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note TEXT NOT NULL,
            created_month TEXT NOT NULL,
            completed_month TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)

        statement_columns = {row[1] for row in self.conn.execute("PRAGMA table_info(statements)")}
        if "import_id" not in statement_columns:
            self.conn.execute("ALTER TABLE statements ADD COLUMN import_id INTEGER REFERENCES statement_imports(id) ON DELETE CASCADE")
        if "loyalty_plan" not in statement_columns:
            self.conn.execute("ALTER TABLE statements ADD COLUMN loyalty_plan TEXT NOT NULL DEFAULT ''")
        