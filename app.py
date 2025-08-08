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


app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this in production

# Initialize database
db = EventDatabase()


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
    print(f"Current event count: {db.get_event_count()}")
    
    # Get port from environment variable (for Railway/Render)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    if debug:
        print("Access the app at: http://localhost:5000")
    
    app.run(debug=debug, host='0.0.0.0', port=port)
