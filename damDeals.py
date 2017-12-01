# This script downloads Amazon Goldbox deals and writes
# both the original and curated (criteria from a csv) deals
# to a csv file

import urllib.request
import shutil
import os
import csv
import re
from xml.dom import minidom
import config
import pickle
from damEmail import send_deals

GOLDBOX_URL = 'https://rssfeeds.s3.amazonaws.com/goldbox'
GOLDBOX_FILE = 'goldbox.xml'
GOLDBOX_CRITERIA = 'deal criteria.txt'
CURATED_DEALS = 'damDeals.p'
TEMP_DEALS = 'damDeals.tmp'

FETCHING_ENABLED = True
EMAIL_ENABLED = True

def dam_Deals():
	# download the goldbox deals to a file and then read
	if FETCHING_ENABLED:
		with urllib.request.urlopen(GOLDBOX_URL) as response, open(GOLDBOX_FILE, 'wb') as goldbox_out:
			shutil.copyfileobj(response, goldbox_out)
	with open(GOLDBOX_FILE, 'r') as file:
		xmldoc = minidom.parseString(file.read())

	# extract the deals and the date that these deals were published (used for output)
	pubDate = getText(xmldoc.getElementsByTagName('pubDate')[0].childNodes)
	itemlist = xmldoc.getElementsByTagName('item') 
	print("Loaded %d items published %s" % (itemlist.length, pubDate))

	# load the criteria we'll use to filter the deals with
	with open(GOLDBOX_CRITERIA, newline='') as file:
		reader = csv.reader(file)
		criteria = list(reader)

	# process each deal item
	dealsDict = {}
	for s in itemlist:
		description = getText(s.getElementsByTagName('description')[0].childNodes).lower()
		if description:
			price = re.search('(?<=deal price: \$)\d+\.\d+', description)
			if price:
				price = price.group(0)
				title = getText(s.getElementsByTagName('title')[0].childNodes).lower()

				# check criteria
				for keywords, maxPrice in criteria:
					# check if every keyword is in the title and that the price is low enough
					if all(map(lambda k: k.casefold() in title.casefold(), keywords.split(' '))) and float(price) <= float(maxPrice):
						link = getText(s.getElementsByTagName('link')[0].childNodes)
						#print("$%s,%s,%s" % (price, title, link))
						dealsDict[title] = [price, link]
						break


	if bool(dealsDict):
		if not os.path.exists(CURATED_DEALS) or not os.path.getsize(CURATED_DEALS) > 0:
			with open(CURATED_DEALS, 'wb') as curatedDeals:
				pickle.dump({}, curatedDeals)

		with open(CURATED_DEALS, 'rb') as curatedDeals:
			oldDeals = pickle.load(curatedDeals)
			if any(map(lambda k: k not in oldDeals or oldDeals[k][0] != dealsDict[k][0], dealsDict.keys())):
				print('New deals found...')
				with open(CURATED_DEALS, 'wb') as curatedDeals:
					pickle.dump(dealsDict, curatedDeals)
				if EMAIL_ENABLED:
					# email the deals that we've found, if there are any
					send_deals(dealsDict)
					return

	print("No new deals found...")


def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

dam_Deals()