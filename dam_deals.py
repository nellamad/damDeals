"""
Retrieves Amazon Goldbox deals and sends a curated
list to subscribers
"""

import argparse
import urllib.request
import shutil
import os
import csv
import re
from xml.dom import minidom
from collections import namedtuple
import config
import pickle
import dam_email

Deal = namedtuple('Deal', ['price', 'title', 'link'])


def dam_deals(args):
    """ Retrieves goldbox deals, curates the deals based on pre-specified criteria
    and then sends emails if necessary."""

    # Retrieve raw deals
    (deals, publish_date) = get_and_parse_deals()
    print("Loaded %d items published %s." % (len(deals), publish_date))

    # Load the criteria used to curate the deals
    with open(config.goldbox_criteria_path, newline='') as file:
        reader = csv.reader(file)
        criteria = list(reader)

    # Build up a collection of curated deals using the criteria from above
    def satisfies_a_criteria(deal):
        # check if the deal all of the criteria's keywords and is below the maximum price
        any([all([keyword.casefold() in deal.title.casefold() for keyword in keywords.split(' ')])
            and float(deal.price) <= float(max_price)
            for keywords, max_price in criteria])
    curated_deals = {title: deal for title, deal in deals.items() if satisfies_a_criteria(deal)}

    # Compare with cached deals and send emails if there are new deals
    cache_and_email(args, curated_deals)


def get_and_parse_deals():
    # download the goldbox deals to a file and then read
    with urllib.request.urlopen(config.goldbox_url) as response, open(config.goldbox_path, 'wb') as goldbox_file:
        shutil.copyfileobj(response, goldbox_file)
    with open(config.goldbox_path, 'r') as goldbox_file:
        xml_doc = minidom.parseString(goldbox_file.read())

    # extract the deals and the date that these deals were published (used for output)
    publish_date = get_text(xml_doc.getElementsByTagName('pubDate')[0].childNodes)
    items = xml_doc.getElementsByTagName('item')
    deals = {}
    for item in items:
        description = get_text(item.getElementsByTagName('description')[0].childNodes).lower()
        price = re.search(r'(?<=deal price: \$)\d+\.\d+', description)
        title = get_text(item.getElementsByTagName('title')[0].childNodes).lower()
        link = get_text(item.getElementsByTagName('link')[0].childNodes)
        if description and price and title and link:
            deals[title] = Deal(price.group(0), title, link)

    return deals, publish_date


def cache_and_email(args, curated_deals):
    if bool(curated_deals):
        old_deals_path = config.old_deals_path
        # initialize/serialize a collection for the old deals, if necessary
        if not os.path.exists(old_deals_path) or not os.path.getsize(old_deals_path) > 0:
            with open(old_deals_path, 'wb') as old_deals:
                pickle.dump({}, old_deals)

        # load and compare old deals with current deals
        with open(old_deals_path, 'rb') as old_deals_file:
            if args.forget_cache:
                old_deals = []
            else:
                old_deals = pickle.load(old_deals_file)
                print('Comparing with old deals...')

            if any([deal.title not in old_deals or old_deals[deal.title].price != deal.price for deal in curated_deals]):
                print('New deals found...')
                if args.verbose:
                    print(curated_deals)

                # store the current deals for the next execution
                with open(old_deals_path, 'wb') as old_deals_file:
                    pickle.dump(curated_deals, old_deals_file)

                if not args.suppress_emails:
                    dam_email.send_deals(args, curated_deals)
                    return

    print("No new deals found...")


def get_text(nodelist):
    """Helper function to extract text from the goldbox xml."""
    texts = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            texts.append(node.data)
    return ''.join(texts)
