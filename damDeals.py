# This script downloads Amazon Goldbox deals and writes
# both the original and curated (criteria from a csv) deals
# to a csv file

import urllib.request
import shutil
import csv
import re
from xml.dom import minidom
import filecmp
import config
import smtplib
from email.message import EmailMessage
from pprint import pprint

GOLDBOX_URL = 'https://rssfeeds.s3.amazonaws.com/goldbox'
GOLDBOX_FILE = 'goldbox.xml'
GOLDBOX_CRITERIA = 'deal criteria.txt'
CURATED_DEALS = 'damDeals.csv'
TEMP_DEALS = 'damDeals.tmp'

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def dam_Deals():
	# download the goldbox deals to a file and then read
	with urllib.request.urlopen(GOLDBOX_URL) as response, open(GOLDBOX_FILE, 'wb') as goldbox_out:
		shutil.copyfileobj(response, goldbox_out)
	with open(GOLDBOX_FILE, 'r') as file:
		xmldoc = minidom.parseString(file.read())

	# load the criteria we'll use to filter the deals with
	with open(GOLDBOX_CRITERIA, newline='') as file:
		reader = csv.reader(file)
		criteria = list(reader)

	# extract the date that these deals were published (used for output)
	pubDate = getText(xmldoc.getElementsByTagName('pubDate')[0].childNodes)

	# process each deal item
	itemlist = xmldoc.getElementsByTagName('item') 
	print("Fetched %d items published %s" % (itemlist.length, pubDate))

	with open(TEMP_DEALS, 'w', newline='') as tempDeals:
		dealsWriter = csv.writer(tempDeals)
		for s in itemlist:
			description = getText(s.getElementsByTagName('description')[0].childNodes).lower()
			if description:
				price = re.search('(?<=deal price: \$)\d+\.\d+', description)
				if price:
					price = price.group(0)
					title = getText(s.getElementsByTagName('title')[0].childNodes).lower()

					# check criteria
					for keyword, maxPrice in criteria:
						if keyword in title and float(price) <= float(maxPrice):
							link = getText(s.getElementsByTagName('link')[0].childNodes)
							#print("$%s,%s,%s" % (price, title, link))
							dealsWriter.writerow([price, title, link])
							break

	try:
		open(CURATED_DEALS, 'x')
	except FileExistsError:
		print("Comparing with old deals...")

	if filecmp.cmp(TEMP_DEALS, CURATED_DEALS, False):
		print("No new deals found...")
	else:
		shutil.copyfile(TEMP_DEALS, CURATED_DEALS)
		send_deals()
		print("New deals found.  Updated list has been sent!")

def send_deals():

	# email the deals that we've found
	with open(CURATED_DEALS) as deals:
		message = EmailMessage()
		message.set_content(deals.read())

	message['Subject'] = 'Your Dam Deals'
	message['From'] = config.GMAIL_USER
	message['To'] = config.SUBSCRIBERS

	server = smtplib.SMTP_SSL('smtp.gmail.com')
	server.login(config.GMAIL_USER, config.GMAIL_PASSWORD)
	server.send_message(message)
	server.quit()

dam_Deals()