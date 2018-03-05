# damDeals

A Python scraper that periodically filters the Amazon Goldbox RSS feed for deals matching a set of custom criteria.  Sends email notifications when new deals are found.
Requires login credentials to an SMTP server to send emails.

## Example usage:

Subscribers are specified in [config.py](https://github.com/nellamad/dam_deals/blob/master/config.py).

Runs the scraper once and sends emails to subscribers if new deals have been found since the last run.
```
dam_deals.py -u foo@bar.com -p p4ssw0rd
```

Runs the scraper immediately and once per hour and sends emails to subscribers if new deals have been found since the last run.
```
dam_deals.py -u foo@bar.com -p p4ssw0rd --hours 1
```

Runs the scraper immediately and once per hour.  Always sends emails to subscribers, even no new deals were found.
```
dam_deals.py -f -u foo@bar.com -p p4ssw0rd --hours 1
```


Full usage:
```
dam_deals.py --help
usage: schedule_cron.py [-h] [-v] [-f] [-s] [--smtp SMTP] [-u USER]
                        [-p PASSWORD] [--hours HOURS | --minutes MINUTES]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity
  -f, --forget_cache    disregard cached deals when deciding whether to send
                        emails
  -s, --suppress_emails
                        suppress email sending
  --smtp SMTP           SMTP email server (default:smtp.gmail.com)
  -u USER, --user USER  email user
  -p PASSWORD, --password PASSWORD
                        email password
  --hours HOURS         schedule a run every number of hours
  --minutes MINUTES     schedule a run every number of minutes
 ```
