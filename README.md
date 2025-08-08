# Waltham Event Discovery App

A web application that discovers and displays fun events happening in Waltham, MA.

## Features

- Scrapes publicly available event listings from 7 local sources
- Stores events in SQLite database with 6-month lookout
- Provides web interface to browse and filter events
- **Daily automatic updates** via scheduled scraping (6 AM & 6 PM)
- Event categorization and filtering
- Mobile-responsive design

## Event Sources

1. **City of Waltham Official Website** - City council meetings, community events, municipal announcements
2. **Waltham Public Library** - Educational programs, book clubs, workshops, family activities
3. **Charles River Museum of Industry & Innovation** - Historical tours, repair cafes, educational workshops, fundraising events
4. **Brandeis University** - Public lectures, art exhibitions, concerts, academic events open to community
5. **Waltham Recreation Department** - Sports leagues, fitness classes, family activities, outdoor programs
6. **Waltham Common** - Farmers market, summer concerts, outdoor fitness, community celebrations
7. **Eventbrite** - Local community events, business workshops, cultural activities
8. **Meetup** - Social groups, hiking clubs, professional networking, hobby groups

## Setup Instructions

1. Clone/download this repository
2. Navigate to the project directory
3. Create a virtual environment: `python3 -m venv .venv`
4. Activate virtual environment: `source .venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Initialize database: `python database.py`
7. Run initial scraping: `python scraper.py`
8. Start the web app: `python app.py`
9. Open browser to `http://localhost:5000`

## File Structure

- `app.py` - Flask web application
- `scraper.py` - Event scraping logic
- `database.py` - Database setup and operations
- `models.py` - Data models
- `templates/` - HTML templates
- `static/` - CSS/JS files
- `requirements.txt` - Python dependencies

## Usage

The web interface allows you to:
- Browse all upcoming events
- Filter by date range
- Filter by category (family, music, outdoors, etc.)
- View event details and source links

## Updating Events

Events are automatically updated twice daily (6 AM and 6 PM) when the scheduler is running.

### Manual Updates:
```bash
python scraper.py
```

### Start Automatic Scheduling:
```bash
python scheduler.py
```

### Production Deployment:
See `DEPLOYMENT.md` for systemd service setup and other production options.
