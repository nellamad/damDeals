"""Handles the creation and execution of the cron
job that wil run dam_deals."""
import argparse
import time
import os
import dam_deals

from apscheduler.schedulers.background import BackgroundScheduler

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--smtp', default='smtp.gmail.com', help='SMTP email server (default:smtp.gmail.com)')
    parser.add_argument('-u', '--user', help='email user')
    parser.add_argument('-p', '--password', help='email password')
    parser.add_argument('-c', '--use_cache', action='store_true', help='exclude deals that were found during last run')
    parser.add_argument('-s', '--suppress_emails', action='store_true', help='suppress email sending')
    schedule_group = parser.add_mutually_exclusive_group()
    schedule_group.add_argument('--hours', type=int, help='schedule a run every number of hours')
    schedule_group.add_argument('--minutes', type=int, help='schedule a run every number of minutes')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
    args = parser.parse_args()

    if not args.suppress_emails and (args.user is None or args.password is None):
        print('Please provide --user and --password arguments or enable the --suppress_emails option')
        parser.print_usage()
    else:
        dam_deals.dam_deals(args)
        if args.hours or args.minutes:
            print('Scheduling needed')
            scheduler = BackgroundScheduler()
            if args.hours:
                scheduler.add_job(dam_deals.dam_deals, 'interval', args=args, hours=args.hours)
            elif args.minutes:
                scheduler.add_job(dam_deals.dam_deals, 'interval', args=args, minutes=args.minutes)

            print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
            try:
                # This is here to simulate application activity (which keeps the main thread alive).
                while True:
                    time.sleep(2)
            except (KeyboardInterrupt, SystemExit):
                # Not strictly necessary if daemonic mode is enabled but should be done if possible
                scheduler.shutdown()

