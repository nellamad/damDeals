"""Handles the creation and execution of the cron
job that wil run dam_deals."""
import time
import os
import dam_deals

from apscheduler.schedulers.background import BackgroundScheduler

if __name__ == '__main__':
    SCHEDULER = BackgroundScheduler()
    # scheduler.add_job(tick, 'interval', minutes=1)
    SCHEDULER.add_job(dam_deals.dam_deals, 'interval', hours=1)
    SCHEDULER.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        SCHEDULER.shutdown()
