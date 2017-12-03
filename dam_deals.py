"""
Retrieves Amazon Goldbox deals and sends a curated
list to subscribers
"""

import urllib.request
import shutil
import os
import csv
import re
from xml.dom import minidom
import pickle
import dam_email

def dam_deals():
    """ Retrieves goldbox deals, extracts a curated list
    and then sends emails if necessary."""

    goldbox_url = 'https://rssfeeds.s3.amazonaws.com/goldbox'
    goldbox_path = 'goldbox.xml'
    goldbox_criteria_path = 'deal criteria.txt'
    old_deals_path = 'dam_deals.p'
    fetching_enabled = True
    email_enabled = True

    # download the goldbox deals to a file and then read
    if fetching_enabled:
        with urllib.request.urlopen(goldbox_url) as response, open(goldbox_path, 'wb') as goldbox_file:
            shutil.copyfileobj(response, goldbox_file)
    with open(goldbox_path, 'r') as goldbox_file:
        xml_doc = minidom.parseString(goldbox_file.read())

    # extract the deals and the date that these deals were published (used for output)
    pub_date = get_text(xml_doc.getElementsByTagName('pubDate')[0].childNodes)
    items = xml_doc.getElementsByTagName('item')
    print("Loaded %d items published %s" % (items.length, pub_date))

    # load the criteria we'll use to filter the deals with
    with open(goldbox_criteria_path, newline='') as file:
        reader = csv.reader(file)
        criteria = list(reader)

    current_deals = {}
    # build up a collection of curated deals using our criteria from above
    for item in items:
        description = get_text(item.getElementsByTagName('description')[0].childNodes).lower()
        if description:
            price = re.search(r'(?<=deal price: \$)\d+\.\d+', description)
            if price:
                price = price.group(0)
                title = get_text(item.getElementsByTagName('title')[0].childNodes).lower()

                # check criteria
                for keywords, max_price in criteria:
                    # check if every keyword is in the title and that the price is low enough
                    if all([key.casefold() in title.casefold() for key in keywords.split(' ')]) and float(price) <= float(max_price):
                        link = get_text(item.getElementsByTagName('link')[0].childNodes)
                        # be careful about changing the structure of this dictionary because
                        # the emailer depends on this structure when unpacking the deals
                        current_deals[title] = [price, link]
                        break

    # if there are any new deals, send them to our subscribers
    if bool(current_deals):
        # initialize/serialize a collection for the old deals, if necessary
        if not os.path.exists(old_deals_path) or not os.path.getsize(old_deals_path) > 0:
            with open(old_deals_path, 'wb') as old_deals:
                pickle.dump({}, old_deals)

        # load and compare old deals with current deals, send emails if necessary
        with open(old_deals_path, 'rb') as old_deals_file:
            old_deals = pickle.load(old_deals_file)
            print('Comparing with old deals...')
            if any(map(lambda k: k not in old_deals or old_deals[k][0] != current_deals[k][0], current_deals.keys())):
                print('New deals found...')

                # store the current deals for the next execution
                with open(old_deals_path, 'wb') as old_deals_file:
                    pickle.dump(current_deals, old_deals_file)

                if email_enabled:
                    dam_email.send_deals(current_deals)
                    return

    print("No new deals found...")


def get_text(nodelist):
    """Helper function to extract text from the goldbox xml."""
    texts = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            texts.append(node.data)
    return ''.join(texts)


dam_deals()
