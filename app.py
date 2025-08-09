"""
Flask web application for Waltham Event Discovery.
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, timedelta
from database import EventDatabase
from models import EVENT_CATEGORIES
from scraper import EventScraper
import threading
import time


app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this in production

# Initialize database
db = EventDatabase()

# Global flag to track if initial scraping is complete
initial_scraping_complete = False
scraping_in_progress = False


def ensure_events_loaded():
    """Ensure events are loaded before serving any requests."""
    global initial_scraping_complete, scraping_in_progress
    
    if initial_scraping_complete:
        return True
    
    # Check if we have recent events
    if db.has_recent_events():
        current_count = db.get_event_count()
        print(f"Found {current_count} recent events in database")
        initial_scraping_complete = True
        return True
    
    # If no recent events, run the scraper
    if not scraping_in_progress:
        current_count = db.get_event_count()
        print(f"Database has {current_count} events but needs refresh. Starting event scraping...")
        scraping_in_progress = True
        
        try:
            scraper = EventScraper()
            scraper.scrape_all_sources()
            initial_scraping_complete = True
            scraping_in_progress = False
            
            new_count = db.get_event_count()
            print(f"Scraping complete! Now have {new_count} events.")
            return True
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            scraping_in_progress = False
            # Still allow the app to run even if scraping fails
            initial_scraping_complete = True
            return True
    
    return False


@app.before_request
def before_request():
    """Run before each request to ensure events are loaded."""
    global scraping_in_progress
    
    # Don't block requests for static files or the update endpoint
    if (request.endpoint and 
        (request.endpoint.startswith('static') or 
         request.endpoint == 'update_events')):
        return
    
    if scraping_in_progress:
        # Return a loading page while scraping is in progress
        return render_template('loading.html')
    
    ensure_events_loaded()


@app.route('/')
def index():
    """Main page showing all events with filtering options."""
    # Get filter parameters
    search_query = request.args.get('search', '').strip()
    category = request.args.get('category', '')
    source = request.args.get('source', '')
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    
    # Convert date strings to datetime objects
    start_date = None
    end_date = None
    
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid start date format')
    
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            # Set end time to end of day
            end_date = end_date.replace(hour=23, minute=59, second=59)
        except ValueError:
            flash('Invalid end date format')
    
    # Start with all events
    events = db.get_all_events()
    
    # Apply search filter
    if search_query:
        search_lower = search_query.lower()
        events = [e for e in events if 
                 search_lower in e.name.lower() or 
                 search_lower in e.location.lower() or 
                 search_lower in e.description.lower() or
                 search_lower in e.source_name.lower()]
    
    # Apply category filter
    if category and category in EVENT_CATEGORIES:
        events = [e for e in events if e.category == category]
    
    # Apply source filter
    if source:
        events = [e for e in events if e.source_name == source]
    
    # Apply date range filters
    if start_date:
        events = [e for e in events if e.date_time and e.date_time >= start_date]
    
    if end_date:
        events = [e for e in events if e.date_time and e.date_time <= end_date]
    
    # Get unique sources for filter dropdown
    all_events = db.get_all_events()
    sources = sorted(list(set(e.source_name for e in all_events)))
    
    return render_template('index.html', 
                         events=events,
                         categories=EVENT_CATEGORIES,
                         sources=sources,
                         search_query=search_query,
                         selected_category=category,
                         selected_source=source,
                         start_date=start_date_str,
                         end_date=end_date_str)


@app.route('/update')
def update_events():
    """Manually trigger event update."""
    def run_scraper():
        scraper = EventScraper()
        scraper.scrape_all_sources()
    
    # Run scraper in background thread to avoid blocking the web interface
    thread = threading.Thread(target=run_scraper)
    thread.daemon = True
    thread.start()
    
    flash('Event update started! This may take a few minutes. Refresh the page to see new events.')
    return redirect(url_for('index'))


@app.route('/event/<int:event_id>')
def event_detail(event_id):
    """Show detailed information for a specific event."""
    try:
        event = db.get_event_by_id(event_id)
        if not event:
            flash('Event not found.', 'error')
            return redirect(url_for('index'))
        
        return render_template('event_detail.html', event=event)
        
    except Exception as e:
        print(f"Error loading event {event_id}: {e}")
        flash('Error loading event details.', 'error')
        return redirect(url_for('index'))


@app.route('/api/events')
def api_events():
    """API endpoint to get events as JSON with search and filtering."""
    search_query = request.args.get('search', '').strip()
    category = request.args.get('category', '')
    source = request.args.get('source', '')
    limit = request.args.get('limit', type=int)
    
    # Start with all events
    events = db.get_all_events()
    
    # Apply search filter
    if search_query:
        search_lower = search_query.lower()
        events = [e for e in events if 
                 search_lower in e.name.lower() or 
                 search_lower in e.location.lower() or 
                 search_lower in e.description.lower() or
                 search_lower in e.source_name.lower()]
    
    # Apply category filter
    if category and category in EVENT_CATEGORIES:
        events = [e for e in events if e.category == category]
    
    # Apply source filter
    if source:
        events = [e for e in events if e.source_name == source]
    
    # Apply limit
    if limit:
        events = events[:limit]
    
    return jsonify([event.to_dict() for event in events])


@app.route('/api/stats')
def api_stats():
    """API endpoint for event statistics."""
    total_events = db.get_event_count()
    
    # Get events by category
    category_counts = {}
    for category in EVENT_CATEGORIES:
        count = len(db.get_events_by_category(category))
        if count > 0:
            category_counts[category] = count
    
    return jsonify({
        'total_events': total_events,
        'categories': category_counts,
        'last_updated': datetime.now().isoformat()
    })


@app.template_filter('strftime')
def strftime_filter(date, format='%Y-%m-%d'):
    """Template filter for date formatting."""
    if date is None:
        return ""
    return date.strftime(format)


@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('error.html', 
                         error_code=404,
                         error_message="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return render_template('error.html',
                         error_code=500,
                         error_message="Internal server error"), 500


if __name__ == '__main__':
    import os
    
    print("Starting Waltham Event Discovery App...")
    
    # Ensure events are loaded before starting the server
    print("Checking event database...")
    ensure_events_loaded()
    
    current_count = db.get_event_count()
    print(f"Ready to serve with {current_count} events!")
    
    # Get port from environment variable (for Railway/Render)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    if debug:
        print("Access the app at: http://localhost:5000")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
