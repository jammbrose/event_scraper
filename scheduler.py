"""
Scheduled task runner for automatic event updates.
Run this script to keep events updated automatically with daily scraping.
"""

import schedule
import time
import logging
from datetime import datetime
from scraper import EventScraper

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def update_events():
    """Function to update events - called by scheduler."""
    logger.info("Starting scheduled event update...")
    
    try:
        scraper = EventScraper()
        scraper.scrape_all_sources()
        logger.info("Event update completed successfully!")
    except Exception as e:
        logger.error(f"Error during scheduled update: {e}")


def main():
    """Main scheduler function with improved scheduling."""
    logger.info("Event Scheduler Started!")
    logger.info("Events will be updated daily at 6:00 AM")
    logger.info("Manual updates can be triggered via web interface")
    logger.info("Press Ctrl+C to stop the scheduler")
    
    # Schedule daily updates at 6:00 AM
    schedule.every().day.at("06:00").do(update_events)
    
    # Optional: Additional update at 6:00 PM for high-activity days
    schedule.every().day.at("18:00").do(update_events)
    
    # Weekly deep clean on Sundays at 3:00 AM
    schedule.every().sunday.at("03:00").do(lambda: update_events())
    
    # Run an initial update
    logger.info("Running initial event update...")
    update_events()
    
    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user.")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
        raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScheduler stopped by user.")
    except Exception as e:
        print(f"Scheduler error: {e}")
