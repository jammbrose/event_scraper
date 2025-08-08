#!/usr/bin/env python3
"""
Quick test of the scheduler functionality.
This demonstrates how the daily scheduling will work.
"""

from scheduler import update_events
import logging

# Set up logging for this test
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    print("Testing daily event update functionality...")
    print("=" * 50)
    
    # Test the update function directly
    update_events()
    
    print("=" * 50)
    print("Daily update test completed!")
    print("In production, this will run automatically at 6:00 AM and 6:00 PM daily.")
    print("To start the continuous scheduler, run: python scheduler.py")
