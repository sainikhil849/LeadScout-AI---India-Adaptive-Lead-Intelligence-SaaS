import sqlite3
import pandas as pd
from pathlib import Path

class DatabaseManager:
    """
    Handles SQLite database persistence for leads.
    Enables caching, deduplication, and efficient retrieval for the SaaS dashboard.
    """
    def __init__(self, db_path: str = "leads.db"):
        # Resolve path relative to project root
        project_root = Path(__file__).resolve().parent.parent
        self.db_file = project_root / db_path
        self._init_db()

    def _get_connection(self):
        # Using check_same_thread=False since Streamlit and Playwright run across threads
        return sqlite3.connect(self.db_file, check_same_thread=False)

    def _init_db(self):
        """Creates the leads table if it doesn't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT,
                    address TEXT,
                    website TEXT,
                    rating REAL,
                    reviews INTEGER,
                    search_category TEXT,
                    city TEXT,
                    source TEXT,
                    score REAL,
                    conversion_prob REAL,
                    priority TEXT,
                    action TEXT,
                    reason TEXT,
                    message TEXT,
                    google_maps_url TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(phone, name)
                )
            ''')
            conn.commit()

    def save_lead(self, lead: dict, city: str):
        """
        Upserts a lead into the database. 
        If phone+name conflict occurs, updates the intelligence fields to keep them fresh.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Normalize missing fields
            phone = lead.get('phone') or ""
            name = lead.get('name') or "Unknown"
            
            cursor.execute('''
                INSERT INTO leads (
                    name, phone, address, website, rating, reviews, search_category, 
                    city, source, score, conversion_prob, priority, action, reason, message, google_maps_url
                ) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(phone, name) DO UPDATE SET 
                    score=excluded.score,
                    conversion_prob=excluded.conversion_prob,
                    priority=excluded.priority,
                    action=excluded.action,
                    reason=excluded.reason,
                    rating=excluded.rating,
                    reviews=excluded.reviews,
                    scraped_at=CURRENT_TIMESTAMP
            ''', (
                name,
                phone,
                lead.get('address'),
                lead.get('website'),
                lead.get('rating'),
                lead.get('reviews'),
                lead.get('search_category'),
                city,
                lead.get('source', 'Unknown Directory'), 
                lead.get('score'),
                lead.get('conversion_prob'),
                lead.get('priority'),
                lead.get('action'),
                lead.get('reason'),
                lead.get('message'),
                lead.get('google_maps_url') or lead.get('profile_url')
            ))
            conn.commit()

    def lead_exists(self, phone: str, name: str) -> bool:
        """Check if a lead already exists in DB to prevent redundant deep scraping."""
        if not phone and not name:
            return False
            
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if phone:
                cursor.execute('SELECT 1 FROM leads WHERE phone = ?', (phone,))
                if cursor.fetchone():
                    return True
            if name:
                cursor.execute('SELECT 1 FROM leads WHERE name = ?', (name,))
                if cursor.fetchone():
                    return True
        return False

    def get_all_leads_df(self) -> pd.DataFrame:
        """Retrieves all leads from the DB as a Pandas DataFrame."""
        with self._get_connection() as conn:
            query = "SELECT * FROM leads ORDER BY score DESC"
            df = pd.read_sql_query(query, conn)
            return df
            
    def get_leads_by_category_city(self, category: str, city: str) -> pd.DataFrame:
        """Retrieves cached leads for a specific search."""
        with self._get_connection() as conn:
            query = "SELECT * FROM leads WHERE search_category LIKE ? AND city LIKE ? ORDER BY score DESC"
            df = pd.read_sql_query(query, conn, params=(f"%{category}%", f"%{city}%"))
            return df
