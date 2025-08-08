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
    
    def init_database(self):
        """Create the events table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
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
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def insert_event(self, event: Event) -> Optional[int]:
        """Insert a new event into the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO events 
                    (name, date_time, location, description, source_url, source_name, category)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    event.name,
                    event.date_time.isoformat() if event.date_time else None,
                    event.location,
                    event.description,
                    event.source_url,
                    event.source_name,
                    event.category
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
        """Retrieve all upcoming events from the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get events for the next 6 months
            query = '''
                SELECT * FROM events 
                WHERE date_time >= datetime('now', 'localtime')
                AND date_time <= datetime('now', '+6 months', 'localtime')
                ORDER BY date_time ASC
            '''
            if limit:
                query += f' LIMIT {limit}'
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            events = []
            for row in rows:
                event = Event(
                    id=row['id'],
                    name=row['name'],
                    date_time=datetime.fromisoformat(row['date_time']) if row['date_time'] else None,
                    location=row['location'],
                    description=row['description'],
                    source_url=row['source_url'],
                    source_name=row['source_name'],
                    category=row['category'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
                events.append(event)
            
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
                event = Event(
                    id=row['id'],
                    name=row['name'],
                    date_time=datetime.fromisoformat(row['date_time']) if row['date_time'] else None,
                    location=row['location'],
                    description=row['description'],
                    source_url=row['source_url'],
                    source_name=row['source_name'],
                    category=row['category'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
                events.append(event)
            
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
                event = Event(
                    id=row['id'],
                    name=row['name'],
                    date_time=datetime.fromisoformat(row['date_time']) if row['date_time'] else None,
                    location=row['location'],
                    description=row['description'],
                    source_url=row['source_url'],
                    source_name=row['source_name'],
                    category=row['category'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
                )
                events.append(event)
            
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
        """Get total number of upcoming events (next 6 months)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM events 
                WHERE date_time >= datetime('now', 'localtime')
                AND date_time <= datetime('now', '+6 months', 'localtime')
            ''')
            return cursor.fetchone()[0]
    
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
