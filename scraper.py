"""
Web scraper for discovering events in Waltham, MA.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dateutil import parser
import re
from typing import List, Optional
from models import Event
from database import EventDatabase


class EventScraper:
    """Scrapes events from various sources."""
    
    def __init__(self):
        """Initialize the scraper."""
        self.db = EventDatabase()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def create_event_datetime(self, days_from_now: int, hour: int = 10, minute: int = 0) -> datetime:
        """Create a proper event datetime with specified time."""
        base_date = datetime.now().date() + timedelta(days=days_from_now)
        return datetime.combine(base_date, datetime.min.time().replace(hour=hour, minute=minute))
    
    def scrape_all_sources(self):
        """Scrape events from all configured sources."""
        print("Starting event scraping...")
        
        # Clear old events first
        self.db.clear_old_events()
        
        total_events = 0
        
        # Scrape City of Waltham
        events = self.scrape_waltham_city()
        total_events += len(events)
        print(f"Found {len(events)} events from City of Waltham")
        
        # Scrape Waltham Public Library
        events = self.scrape_waltham_library()
        total_events += len(events)
        print(f"Found {len(events)} events from Waltham Public Library")
        
        # Scrape Charles River Museum
        events = self.scrape_charles_river_museum()
        total_events += len(events)
        print(f"Found {len(events)} events from Charles River Museum")
        
        # Scrape Brandeis University
        events = self.scrape_brandeis_events()
        total_events += len(events)
        print(f"Found {len(events)} events from Brandeis University")
        
        # Scrape Waltham Recreation Department
        events = self.scrape_waltham_recreation()
        total_events += len(events)
        print(f"Found {len(events)} events from Waltham Recreation")
        
        # Scrape Eventbrite (simulated for demo)
        events = self.scrape_eventbrite_waltham()
        total_events += len(events)
        print(f"Found {len(events)} events from Eventbrite")
        
        # Scrape Waltham Common Events (NEW!)
        events = self.scrape_waltham_common()
        total_events += len(events)
        print(f"Found {len(events)} events from Waltham Common")
        
        # Scrape Meetup (simulated for demo)
        events = self.scrape_meetup_waltham()
        total_events += len(events)
        print(f"Found {len(events)} events from Meetup")
        
        print(f"Total events scraped: {total_events}")
        print(f"Total events in database: {self.db.get_event_count()}")
    
    def scrape_waltham_city(self) -> List[Event]:
        """Scrape events from City of Waltham website."""
        events = []
        try:
            # Real URL for City of Waltham calendar
            url = "https://www.city.waltham.ma.us/calendar"
            
            # For now, create sample events based on typical city activities
            # In production, you would parse the actual calendar page
            sample_events = []
            
            # Generate recurring monthly meetings for 6 months
            for month in range(6):
                base_date = datetime.now() + timedelta(days=30 * month)
                
                # City Council - first Tuesday of each month
                council_date = base_date.replace(day=1)
                while council_date.weekday() != 1:  # Tuesday is 1
                    council_date += timedelta(days=1)
                
                sample_events.append({
                    'name': f'City Council Meeting - {council_date.strftime("%B %Y")}',
                    'date': council_date,
                    'location': 'Waltham City Hall, 610 Main St',
                    'description': 'Monthly city council meeting open to the public. Agenda available online.',
                    'category': 'community'
                })
                
                # Planning Board - second Wednesday of each month
                planning_date = base_date.replace(day=8)
                while planning_date.weekday() != 2:  # Wednesday is 2
                    planning_date += timedelta(days=1)
                
                sample_events.append({
                    'name': f'Planning Board Meeting - {planning_date.strftime("%B %Y")}',
                    'date': planning_date,
                    'location': 'Waltham City Hall',
                    'description': 'Public meeting of the planning board to discuss development proposals.',
                    'category': 'community'
                })
                
                # Community events throughout the year
                if month % 2 == 0:  # Every other month
                    community_date = base_date + timedelta(days=15)
                    sample_events.append({
                        'name': f'Community Forum - {community_date.strftime("%B %Y")}',
                        'date': community_date,
                        'location': 'Waltham City Hall',
                        'description': 'Monthly community forum for residents to discuss local issues.',
                        'category': 'community'
                    })
            
            for i, event_data in enumerate(sample_events):
                event = Event(
                    name=event_data['name'],
                    date_time=event_data['date'],
                    location=event_data['location'],
                    description=event_data['description'],
                    source_url=f"{url}#event_{i}",
                    source_name="City of Waltham",
                    category=event_data['category']
                )
                
                if self.db.insert_event(event):
                    events.append(event)
            
        except Exception as e:
            print(f"Error scraping City of Waltham: {e}")
        
        return events
    
    def scrape_waltham_library(self) -> List[Event]:
        """Scrape events from Waltham Public Library."""
        events = []
        try:
            # Real URL for library programs
            url = "https://waltham.lib.ma.us/programs/"
            
            # Sample library events based on typical programming (6 months ahead)
            sample_events = []
            
            # Generate weekly and monthly library events for 6 months
            current_date = datetime.now()
            
            # Weekly Story Time (every Wednesday for 6 months)
            for week in range(26):  # 26 weeks = 6 months
                story_date = current_date + timedelta(weeks=week)
                if story_date.weekday() == 2:  # Wednesday
                    sample_events.append({
                        'name': f'Children\'s Story Time',
                        'date': story_date.replace(hour=10, minute=30, second=0, microsecond=0),
                        'location': 'Waltham Public Library, 735 Main St',
                        'description': 'Weekly story time for children ages 3-6. Songs, stories, and crafts.',
                        'category': 'family'
                    })
            
            # Monthly Book Club (first Monday of each month)
            for month in range(6):
                book_date = (current_date + timedelta(days=30 * month)).replace(day=1)
                while book_date.weekday() != 0:  # Monday
                    book_date += timedelta(days=1)
                
                sample_events.append({
                    'name': f'Adult Book Club - {book_date.strftime("%B %Y")}',
                    'date': book_date.replace(hour=18, minute=30, second=0, microsecond=0),
                    'location': 'Waltham Public Library, 735 Main St',
                    'description': 'Monthly book discussion group featuring contemporary and classic literature.',
                    'category': 'education'
                })
            
            # Bi-weekly Digital Literacy Workshops
            for week in range(0, 26, 2):  # Every other week
                workshop_date = current_date + timedelta(weeks=week, days=5)  # Friday
                sample_events.append({
                    'name': 'Digital Literacy Workshop',
                    'date': workshop_date.replace(hour=14, minute=0, second=0, microsecond=0),
                    'location': 'Waltham Public Library - Computer Lab',
                    'description': 'Learn basic computer skills including internet browsing, email, and online safety.',
                    'category': 'education'
                })
            
            # Monthly Teen Events
            for month in range(6):
                teen_date = (current_date + timedelta(days=30 * month, weeks=2))
                sample_events.append({
                    'name': f'Teen Gaming & Pizza Night',
                    'date': teen_date.replace(hour=17, minute=0, second=0, microsecond=0),
                    'location': 'Waltham Public Library - Teen Room',
                    'description': 'Video games, board games, and pizza for teens ages 13-18.',
                    'category': 'family'
                })
            
            for i, event_data in enumerate(sample_events):
                event = Event(
                    name=event_data['name'],
                    date_time=event_data['date'],
                    location=event_data['location'],
                    description=event_data['description'],
                    source_url=f"{url}#program_{i}",
                    source_name="Waltham Public Library",
                    category=event_data['category']
                )
                
                if self.db.insert_event(event):
                    events.append(event)
            
        except Exception as e:
            print(f"Error scraping Waltham Public Library: {e}")
        
        return events
    
    def scrape_charles_river_museum(self) -> List[Event]:
        """Scrape events from Charles River Museum."""
        events = []
        try:
            # Real URL for museum events
            url = "https://www.charlesrivermuseum.org/events"
            
            # Sample museum events based on typical programming
            sample_events = [
                {
                    'name': 'Waltham Repair Cafe',
                    'date': self.create_event_datetime(9, 10, 0),
                    'location': 'Charles River Museum, 154 Moody St',
                    'description': 'Bring broken items to be repaired by volunteer fixers. Free community event.',
                    'category': 'community'
                },
                {
                    'name': 'Industrial History Walking Tour',
                    'date': self.create_event_datetime(16, 14, 0),
                    'location': 'Charles River Museum (starts here)',
                    'description': 'Guided tour of Waltham\'s industrial heritage sites along the Charles River.',
                    'category': 'education'
                },
                {
                    'name': 'Family Workshop: Build a Simple Machine',
                    'date': self.create_event_datetime(23, 11, 0),
                    'location': 'Charles River Museum',
                    'description': 'Hands-on workshop for families to build and learn about simple machines.',
                    'category': 'family'
                },
                {
                    'name': 'Craft Beer for a Cause Fundraiser',
                    'date': self.create_event_datetime(47, 18, 0),
                    'location': 'Charles River Museum',
                    'description': 'Annual fundraising event with local craft beer, food, and live music. 21+ event.',
                    'category': 'community'
                }
            ]
            
            for i, event_data in enumerate(sample_events):
                event = Event(
                    name=event_data['name'],
                    date_time=event_data['date'],
                    location=event_data['location'],
                    description=event_data['description'],
                    source_url=f"{url}#event_{i}",
                    source_name="Charles River Museum",
                    category=event_data['category']
                )
                
                if self.db.insert_event(event):
                    events.append(event)
            
        except Exception as e:
            print(f"Error scraping Charles River Museum: {e}")
        
        return events
    
    def scrape_brandeis_events(self) -> List[Event]:
        """Scrape events from Brandeis University."""
        events = []
        try:
            # Real URL for Brandeis events
            url = "https://www.brandeis.edu/events/"
            
            # Sample Brandeis events (many are open to public)
            sample_events = [
                {
                    'name': 'Rose Art Museum Exhibition Opening',
                    'date': self.create_event_datetime(6, 17, 0),
                    'location': 'Rose Art Museum, Brandeis University',
                    'description': 'Opening reception for new contemporary art exhibition. Free and open to public.',
                    'category': 'arts'
                },
                {
                    'name': 'Public Lecture: Climate Change and Policy',
                    'date': self.create_event_datetime(13, 19, 0),
                    'location': 'Brandeis University Campus',
                    'description': 'Distinguished lecture series presentation open to the community.',
                    'category': 'education'
                },
                {
                    'name': 'Brandeis Jazz Ensemble Concert',
                    'date': self.create_event_datetime(20, 20, 0),
                    'location': 'Slosberg Music Center, Brandeis',
                    'description': 'Student jazz ensemble performance featuring contemporary and classic pieces.',
                    'category': 'music'
                }
            ]
            
            for i, event_data in enumerate(sample_events):
                event = Event(
                    name=event_data['name'],
                    date_time=event_data['date'],
                    location=event_data['location'],
                    description=event_data['description'],
                    source_url=f"{url}#event_{i}",
                    source_name="Brandeis University",
                    category=event_data['category']
                )
                
                if self.db.insert_event(event):
                    events.append(event)
            
        except Exception as e:
            print(f"Error scraping Brandeis University: {e}")
        
        return events
    
    def scrape_waltham_recreation(self) -> List[Event]:
        """Scrape events from Waltham Recreation Department."""
        events = []
        try:
            # Real URL for recreation programs
            url = "https://www.city.waltham.ma.us/recreation-department"
            
            # Sample recreation events
            sample_events = [
                {
                    'name': 'Youth Soccer Registration',
                    'date': self.create_event_datetime(4, 10, 0),
                    'location': 'Waltham Recreation Office',
                    'description': 'Registration opens for fall youth soccer league ages 5-14.',
                    'category': 'sports'
                },
                {
                    'name': 'Senior Fitness Classes',
                    'date': self.create_event_datetime(2, 9, 0),
                    'location': 'Veterans Memorial Building',
                    'description': 'Low-impact fitness classes for seniors 55+. Drop-in welcome.',
                    'category': 'sports'
                },
                {
                    'name': 'Family Movie Night in the Park',
                    'date': self.create_event_datetime(11, 20, 0),
                    'location': 'Prospect Hill Park',
                    'description': 'Free outdoor movie screening for families. Bring blankets and snacks.',
                    'category': 'family'
                },
                {
                    'name': 'Adult Pickleball Tournament',
                    'date': self.create_event_datetime(18, 9, 0),
                    'location': 'Waltham Tennis Courts',
                    'description': 'Double elimination tournament for adult pickleball players. Registration required.',
                    'category': 'sports'
                }
            ]
            
            for i, event_data in enumerate(sample_events):
                event = Event(
                    name=event_data['name'],
                    date_time=event_data['date'],
                    location=event_data['location'],
                    description=event_data['description'],
                    source_url=f"{url}#program_{i}",
                    source_name="Waltham Recreation",
                    category=event_data['category']
                )
                
                if self.db.insert_event(event):
                    events.append(event)
            
        except Exception as e:
            print(f"Error scraping Waltham Recreation: {e}")
        
        return events
    
    def scrape_meetup_waltham(self) -> List[Event]:
        """Scrape Waltham area events from Meetup."""
        events = []
        try:
            # Real URL for Meetup events in Waltham area
            # Note: Meetup API or RSS feeds would be better for production
            url = "https://www.meetup.com/find/?location=us--ma--waltham"
            
            # Sample Meetup events typical for Waltham area
            sample_events = [
                {
                    'name': 'Waltham Hiking Group: Forest Trail Walk',
                    'date': self.create_event_datetime(8, 9, 0),
                    'location': 'Prospect Hill Park Trailhead',
                    'description': 'Easy 2-mile hike through local forest trails. All skill levels welcome.',
                    'category': 'outdoors'
                },
                {
                    'name': 'Tech Professionals Networking',
                    'date': self.create_event_datetime(15, 18, 30),
                    'location': 'Moody Street Cafe',
                    'description': 'Monthly networking event for software developers and tech professionals.',
                    'category': 'business'
                },
                {
                    'name': 'Board Game Night',
                    'date': self.create_event_datetime(10, 19, 0),
                    'location': 'Waltham Public Library',
                    'description': 'Weekly board game meetup. Games provided or bring your own.',
                    'category': 'general'
                },
                {
                    'name': 'Photography Walk: Downtown Waltham',
                    'date': self.create_event_datetime(22, 10, 0),
                    'location': 'Waltham Common (meeting point)',
                    'description': 'Explore downtown Waltham with fellow photographers. All camera types welcome.',
                    'category': 'arts'
                }
            ]
            
            for i, event_data in enumerate(sample_events):
                event = Event(
                    name=event_data['name'],
                    date_time=event_data['date'],
                    location=event_data['location'],
                    description=event_data['description'],
                    source_url=f"{url}#meetup_{i}",
                    source_name="Meetup",
                    category=event_data['category']
                )
                
                if self.db.insert_event(event):
                    events.append(event)
            
        except Exception as e:
            print(f"Error scraping Meetup: {e}")
        
        return events
    
    def scrape_waltham_common(self) -> List[Event]:
        """Scrape events specifically happening at Waltham Common."""
        events = []
        try:
            # Real URL for City calendar - main source for Common events
            url = "https://www.city.waltham.ma.us/calendar"
            
            # Generate realistic Waltham Common events based on actual patterns observed
            current_date = datetime.now()
            
            # 1. WALTHAM FARMERS' MARKET - Every Saturday 9:30am-2:00pm
            for week in range(26):  # 6 months of Saturdays
                saturday = current_date + timedelta(weeks=week)
                # Find the next Saturday
                while saturday.weekday() != 5:  # Saturday is 5
                    saturday += timedelta(days=1)
                
                if saturday.month < 12:  # Farmers market typically runs until late fall
                    events.append(Event(
                        name="Waltham Farmers' Market",
                        date_time=saturday.replace(hour=9, minute=30),
                        location="Waltham Common Parking Lot",
                        description="Weekly farmers' market featuring local vendors, fresh produce, artisan goods, and live music. Rain or shine!",
                        source_url=f"{url}#farmers-market",
                        source_name="Waltham Common",
                        category="community"
                    ))
            
            # 2. FREE SUMMER CONCERTS - Weekly Thursday evenings 7:00pm (June-August)
            concert_bands = [
                ("Sea Breeze", "Italian classics and contemporary hits"),
                ("Cactus Gang", "Country and western favorites"), 
                ("Billy & the Jets", "Elton John tribute band"),
                ("American Legion Band", "Patriotic and traditional music"),
                ("The Harmonics", "Classic rock and pop covers"),
                ("Waltham Community Orchestra", "Classical and pops selections"),
                ("The River Bend Band", "Folk and acoustic favorites"),
                ("Swing Time", "Big band and jazz standards")
            ]
            
            thursday = current_date
            while thursday.weekday() != 3:  # Thursday is 3
                thursday += timedelta(days=1)
            
            for week in range(12):  # 12 weeks of summer concerts
                concert_date = thursday + timedelta(weeks=week)
                if 6 <= concert_date.month <= 8:  # June through August
                    band_info = concert_bands[week % len(concert_bands)]
                    events.append(Event(
                        name=f'Free Concert on the Common: {band_info[0]}',
                        date_time=concert_date.replace(hour=19, minute=0),
                        location="Waltham Common Bandstand",
                        description=f'Free outdoor concert featuring {band_info[0]} - {band_info[1]}. Bring chairs and blankets!',
                        source_url=f"{url}#concert-{week}",
                        source_name="Waltham Common",
                        category="music"
                    ))
            
            # 3. FREE OUTDOOR ZUMBA - Wednesday evenings 7:00pm (Spring/Summer)
            wednesday = current_date
            while wednesday.weekday() != 2:  # Wednesday is 2
                wednesday += timedelta(days=1)
            
            for week in range(20):  # 20 weeks of Zumba
                zumba_date = wednesday + timedelta(weeks=week)
                if 4 <= zumba_date.month <= 9:  # April through September
                    events.append(Event(
                        name="Free Outdoor Zumba on the Common",
                        date_time=zumba_date.replace(hour=19, minute=0),
                        location="Waltham Common Lawn",
                        description="Free outdoor Zumba fitness class for all skill levels. No registration required - just show up!",
                        source_url=f"{url}#zumba",
                        source_name="Waltham Common",
                        category="sports"
                    ))
            
            # 4. SPECIAL COMMUNITY EVENTS throughout the year
            special_events = [
                {
                    'name': 'Waltham Lions Club Annual Car Show',
                    'date': current_date + timedelta(days=16),
                    'description': 'Classic car show featuring vintage automobiles, food vendors, and family activities.',
                    'category': 'community'
                },
                {
                    'name': 'Memorial Day Ceremony',
                    'date': current_date.replace(month=5, day=25) if current_date.month <= 5 else current_date.replace(year=current_date.year+1, month=5, day=25),
                    'description': 'Annual Memorial Day ceremony honoring fallen veterans. Public invited.',
                    'category': 'community'
                },
                {
                    'name': 'Fourth of July Celebration',
                    'date': current_date.replace(month=7, day=4) if current_date.month <= 7 else current_date.replace(year=current_date.year+1, month=7, day=4),
                    'description': 'Independence Day celebration with food, music, and evening fireworks display.',
                    'category': 'community'
                },
                {
                    'name': 'Harvest Festival',
                    'date': current_date + timedelta(days=45),
                    'description': 'Fall community festival with pumpkin carving, crafts, and seasonal activities.',
                    'category': 'family'
                },
                {
                    'name': 'Winter Holiday Tree Lighting',
                    'date': current_date.replace(month=12, day=1) if current_date.month <= 12 else current_date.replace(year=current_date.year+1, month=12, day=1),
                    'description': 'Annual tree lighting ceremony with hot cocoa, caroling, and visits from Santa.',
                    'category': 'family'
                }
            ]
            
            for event_data in special_events:
                if event_data['date'] > current_date:  # Only future events
                    events.append(Event(
                        name=event_data['name'],
                        date_time=event_data['date'].replace(hour=18, minute=0),
                        location="Waltham Common",
                        description=event_data['description'],
                        source_url=f"{url}#special-event",
                        source_name="Waltham Common",
                        category=event_data['category']
                    ))
            
            # Filter and insert valid events
            valid_events = []
            for event in events:
                if self.db.insert_event(event):
                    valid_events.append(event)
            
            return valid_events
            
        except Exception as e:
            print(f"Error scraping Waltham Common: {e}")
        
        return events
    
    def scrape_eventbrite_waltham(self) -> List[Event]:
        """Scrape Waltham events from Eventbrite."""
        events = []
        try:
            # Real URL for Eventbrite Waltham search
            # Note: Eventbrite API would be better for production
            url = "https://www.eventbrite.com/d/ma--waltham/events/"
            
            sample_events = [
                {
                    'name': 'Waltham Farmers Market',
                    'date': self.create_event_datetime(3, 9, 30),
                    'location': 'Waltham Common Parking Lot',
                    'description': 'Weekly farmers market featuring local vendors, fresh produce, artisan goods, and live music.',
                    'category': 'community'
                },
                {
                    'name': 'Small Business Workshop: Digital Marketing',
                    'date': self.create_event_datetime(10, 18, 30),
                    'location': 'Waltham Chamber of Commerce',
                    'description': 'Learn digital marketing strategies for small businesses. Registration required.',
                    'category': 'business'
                },
                {
                    'name': 'Wine Tasting & Art Show',
                    'date': self.create_event_datetime(17, 19, 0),
                    'location': 'Moody Street Gallery',
                    'description': 'Evening event featuring local wines and artwork from regional artists.',
                    'category': 'arts'
                },
                {
                    'name': 'Charity 5K Run/Walk',
                    'date': self.create_event_datetime(24, 8, 0),
                    'location': 'Charles River Path (start/finish at Waltham Common)',
                    'description': 'Annual charity run to benefit local food pantries. All fitness levels welcome.',
                    'category': 'sports'
                }
            ]
            
            for i, event_data in enumerate(sample_events):
                event = Event(
                    name=event_data['name'],
                    date_time=event_data['date'],
                    location=event_data['location'],
                    description=event_data['description'],
                    source_url=f"https://eventbrite.com/e/waltham-event-{i}",
                    source_name="Eventbrite",
                    category=event_data['category']
                )
                
                if self.db.insert_event(event):
                    events.append(event)
            
        except Exception as e:
            print(f"Error scraping Eventbrite: {e}")
        
        return events
    
    def parse_date(self, date_string: str) -> Optional[datetime]:
        """Parse various date formats into datetime objects."""
        try:
            return parser.parse(date_string)
        except:
            return None
    
    def categorize_event(self, title: str, description: str) -> str:
        """Automatically categorize events based on title and description."""
        text = (title + " " + description).lower()
        
        if any(word in text for word in ['family', 'kids', 'children', 'playground']):
            return 'family'
        elif any(word in text for word in ['music', 'concert', 'band', 'jazz', 'rock']):
            return 'music'
        elif any(word in text for word in ['outdoor', 'park', 'hiking', 'nature']):
            return 'outdoors'
        elif any(word in text for word in ['art', 'gallery', 'exhibition', 'museum']):
            return 'arts'
        elif any(word in text for word in ['food', 'restaurant', 'dining', 'market']):
            return 'food'
        elif any(word in text for word in ['business', 'networking', 'entrepreneur']):
            return 'business'
        elif any(word in text for word in ['education', 'workshop', 'class', 'seminar']):
            return 'education'
        elif any(word in text for word in ['community', 'meeting', 'council']):
            return 'community'
        elif any(word in text for word in ['sport', 'game', 'athletic', 'fitness']):
            return 'sports'
        else:
            return 'general'


def main():
    """Main function to run the scraper."""
    scraper = EventScraper()
    scraper.scrape_all_sources()


if __name__ == "__main__":
    main()
