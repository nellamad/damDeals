"""
Retrieves Amazon Goldbox deals and sends a curated
list to subscribers
"""
import os
import csv
import config
from data_retrieval import get_and_parse_deals
import pickle
from emailer import send_deals


def dam_deals(args):
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
        return any([all([keyword.casefold() in deal.title.casefold() for keyword in keywords.split(' ')])
                    and float(deal.price) <= float(max_price)
                    for keywords, max_price in criteria])
    curated_deals = {title: deal for title, deal in deals.items() if satisfies_a_criteria(deal)}

    # Compare with cached deals and send emails if there are new deals
    cache_and_email(args, curated_deals)


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
                    send_deals(args, curated_deals)
                    return

    print("No new deals found...")

