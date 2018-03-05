import urllib.request
import shutil
import re
from xml.dom import minidom
import config
from collections import namedtuple

Deal = namedtuple('Deal', ['price', 'title', 'link'])


def get_and_parse_deals():
    def get_text(nodelist):
        """Helper function to extract text from the goldbox xml."""
        texts = []
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                texts.append(node.data)
        return ''.join(texts)

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
