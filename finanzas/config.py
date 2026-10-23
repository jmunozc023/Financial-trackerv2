from pathlib import Path
import os

APP_NAME = "FinnTracker" # Define the application name
DATA_DIR = Path(os.environ.get("APPDATA", str(Path.home()))) / APP_NAME # Define the data directory path based on the operating system
DATA_DIR.mkdir(parents=True, exist_ok=True) # Create the data directory if it doesn't exist
DB_PATH = DATA_DIR / "finntracker.db" # Define the database file path
MONTHS = [f"{year:04d}-{month:02d}" for year in range(2020, 2051) for month in range(1, 13)] # Generate a list of months from 2020 to 2050 in the format YYYY-MM

BG = "#f4f6f8"
CARD = "#ffffff"
INK = "#16212b"
MUTED = "#687582"
NAV = "#142b3b"
ACCENT = "#087e72"
RED = "#bd4c49"
GREEN = "#168267"