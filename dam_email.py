"""
Email module which handles the crafting and sending of emails.
"""
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from tabulate import tabulate
import config

def send_deals(deals):
    """Creates an email from the given deals, then sends them to subscribers.
    Meant to use the Deal class from the dam_deals module"""
    headers = [['Price', 'Link']]
    text = '{table}'
    html = """
    <html>
        <body>
            {table}
        </body>
    </html>
    """

    deals = [(deal.price, deal.title, deal.link) for deal in deals.values()]
    text = text.format(table=tabulate(headers + deals, headers='firstrow', tablefmt='grid'))
    html = html.format(table=tabulate(
        headers +  [(r[0], '<a href="{1}" target="_blank">{0}</a>'.format(r[1], r[2])) for r in deals],
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
