"""
Database operations for the event scraper application.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional
from models import Event


class EventDatabase:
    """Handles all database operations for events."""
    
    def __init__(self, db_path: str = "events.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self.init_database()
    
    def _row_to_event(self, row) -> Event:
        """Convert a database row to an Event object."""
        # Handle both dict-like and Row objects
        def safe_get(key, default=''):
            try:
                return row[key] if row[key] is not None else default
            except (KeyError, TypeError):
                return default
        
        return Event(
            id=safe_get('id', 0),
            name=safe_get('name'),
            date_time=datetime.fromisoformat(row['date_time']) if row['date_time'] else None,
            location=safe_get('location'),
            description=safe_get('description'),
            source_url=safe_get('source_url'),
            source_name=safe_get('source_name'),
            category=safe_get('category', 'general'),
            cost=safe_get('cost'),
            organizer=safe_get('organizer'),
            contact_info=safe_get('contact_info'),
            registration_required=bool(safe_get('registration_required', False)),
            age_restrictions=safe_get('age_restrictions'),
            created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
        )
    
    def init_database(self):
        """Create the events table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            # First create the table with basic structure
            conn.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    date_time DATETIME,
                    location TEXT,
                    description TEXT,
                    source_url TEXT UNIQUE,
                    source_name TEXT,
                    category TEXT DEFAULT 'general',
                    cost TEXT DEFAULT '',
                    organizer TEXT DEFAULT '',
                    contact_info TEXT DEFAULT '',
                    registration_required BOOLEAN DEFAULT 0,
                    age_restrictions TEXT DEFAULT '',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Add new columns if they don't exist (for existing databases)
            try:
                conn.execute('ALTER TABLE events ADD COLUMN cost TEXT DEFAULT ""')
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            try:
                conn.execute('ALTER TABLE events ADD COLUMN organizer TEXT DEFAULT ""')
            except sqlite3.OperationalError:
                pass
                
            try:
                conn.execute('ALTER TABLE events ADD COLUMN contact_info TEXT DEFAULT ""')
            except sqlite3.OperationalError:
                pass
                
            try:
                conn.execute('ALTER TABLE events ADD COLUMN registration_required BOOLEAN DEFAULT 0')
            except sqlite3.OperationalError:
                pass
                
            try:
                conn.execute('ALTER TABLE events ADD COLUMN age_restrictions TEXT DEFAULT ""')
            except sqlite3.OperationalError:
                pass
            
            conn.commit()
    
    def insert_event(self, event: Event) -> Optional[int]:
        """Insert a new event into the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO events 
                    (name, date_time, location, description, source_url, source_name, category,
                     cost, organizer, contact_info, registration_required, age_restrictions)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.name,
                    event.date_time.isoformat() if event.date_time else None,
                    event.location,
                    event.description,
                    event.source_url,
                    event.source_name,
                    event.category,
                    event.cost,
                    event.organizer,
                    event.contact_info,
                    event.registration_required,
                    event.age_restrictions
                ))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Event with this URL already exists
            return None
        except Exception as e:
            print(f"Error inserting event: {e}")
            return None
    
    def get_all_events(self, limit: Optional[int] = None) -> List[Event]:
        """Retrieve all events from the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if limit:
                cursor.execute('''
                    SELECT * FROM events 
                    WHERE date_time >= datetime('now', 'localtime')
                    ORDER BY date_time ASC 
                    LIMIT ?
                ''', (limit,))
            else:
                cursor.execute('''
                    SELECT * FROM events 
                    WHERE date_time >= datetime('now', 'localtime')
                    ORDER BY date_time ASC
                ''')
            rows = cursor.fetchall()
            
            events = []
            for row in rows:
                events.append(self._row_to_event(row))
            
            return events
    
    def get_events_by_category(self, category: str) -> List[Event]:
        """Retrieve events filtered by category."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM events 
                WHERE category = ? AND date_time >= datetime('now', 'localtime')
                ORDER BY date_time ASC
            ''', (category,))
            rows = cursor.fetchall()
            
            events = []
            for row in rows:
                events.append(self._row_to_event(row))
            
            return events
    
    def get_events_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Event]:
        """Retrieve events within a specific date range."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM events 
                WHERE date_time BETWEEN ? AND ?
                ORDER BY date_time ASC
            ''', (start_date.isoformat(), end_date.isoformat()))
            rows = cursor.fetchall()
            
            events = []
            for row in rows:
                events.append(self._row_to_event(row))
            
            return events
    
    def clear_old_events(self):
        """Remove events that have already passed."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM events 
                WHERE date_time < datetime('now', 'localtime')
            ''')
            deleted_count = cursor.rowcount
            conn.commit()
            print(f"Removed {deleted_count} past events from database")
    
    def get_event_count(self) -> int:
        """Get the total count of events in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM events WHERE date_time >= datetime("now", "localtime")')
            return cursor.fetchone()[0]
    
    def get_event_by_id(self, event_id: int) -> Optional[Event]:
        """Get a specific event by its ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM events WHERE id = ?
            ''', (event_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return self._row_to_event(row)
    
    def has_recent_events(self, hours: int = 24) -> bool:
        """Check if we have events that were added in the last N hours."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM events 
                WHERE created_at >= datetime('now', '-{} hours', 'localtime')
                AND date_time >= datetime('now', 'localtime')
            '''.format(hours))
            recent_count = cursor.fetchone()[0]
            
            # Also check total upcoming event count
            total_count = self.get_event_count()
            
            # Consider database "fresh" if we have recent events or a good number of total events
            return recent_count > 0 or total_count > 10


if __name__ == "__main__":
    # Initialize database when run directly
    db = EventDatabase()
    print("Database initialized successfully!")
    print(f"Current event count: {db.get_event_count()}")
