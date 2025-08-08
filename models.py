"""
Data models for the event scraper application.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Event:
    """Represents a single event."""
    
    id: Optional[int] = None
    name: str = ""
    date_time: Optional[datetime] = None
    location: str = ""
    description: str = ""
    source_url: str = ""
    source_name: str = ""
    category: str = "general"
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self):
        """Convert event to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'date_time': self.date_time.isoformat() if self.date_time else None,
            'location': self.location,
            'description': self.description,
            'source_url': self.source_url,
            'source_name': self.source_name,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Event categories for filtering
EVENT_CATEGORIES = [
    'general',
    'family',
    'music',
    'outdoors',
    'sports',
    'arts',
    'food',
    'business',
    'education',
    'community'
]
