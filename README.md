# damDeals
Periodically checks Amazon Goldbox deals and sends emails containing deals that fit your criteria

Utilizes Gmail's SMTP server for email functionality and therefore requires Gmail credentaials.

How to use:
1. Create a config.py file with email credentials and subscriber list. Sample contents:
	GMAIL_USER = 'foo@gmail.com'
	GMAIL_PASSWORD = 'bar'
	SUBSCRIBERS = 'john@gmail.com, smith@gmail.com'
2. Edit the deal_criteria file to include the deals you want to watch for.  Each row should include:
  a. An exact keyword or phrase to search for in a deal's title
  b. A deal's maximum price
3. Run the dealDeals.py script for a one-time check.  Run scheduleCron.py to have a background scheduler execute the checks every hour.

The script generates a couple files including the final filtered list of deals (damDeals.csv).  Although the cron executes periodically, emails will only be sent if this list includes any changes.