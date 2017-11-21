import config
import csv
from tabulate import tabulate
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def send_deals(deals_file):
	headers = [['Price', 'Link']]
	text = '{table}'
	html = """
	<html>
		<body>
			{table}
		</body>
	</html>
	"""
	reader = csv.reader(deals_file)
	deals = list(reader)
	text = text.format(table=tabulate(headers + deals, headers='firstrow', tablefmt='grid'))
	html = html.format(table=tabulate(
		headers + list(map(lambda r: [
				r[0],
				'<a href="{1}" target="_blank">{0}</a>'.format(r[1], r[2])
			],
			deals)),
		headers='firstrow',
		tablefmt='html')
	)

	message = MIMEMultipart('alternative', None, [MIMEText(text), MIMEText(html, 'html')])
	message['Subject'] = 'Your Dam Deals'
	message['From'] = config.GMAIL_USER
	message['To'] = config.SUBSCRIBERS

	server = smtplib.SMTP_SSL(config.SMTP_SERVER)
	server.login(config.GMAIL_USER, config.GMAIL_PASSWORD)
	server.send_message(message)
	server.quit()

	print('Updated list has been sent!')