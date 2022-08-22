#!/usr/bin/python

import datetime  # used for naming, can be replaced
import time  # used for naming, can be replaced
from bs4 import BeautifulSoup as BS
import requests
import re
import os
import logging
import csv


class Parser:
    def __init__(self):
        self.item_link = None  # link to the current item parsed
        self.image_link = None  # link to the current item's image parsed
        self.body = None  # html body of the current page
        self.link = None  # link to the current page
        self.soup = None  # parsed http response
        self.response = None  # http response
        self.page = 1  # current page number
        self.item = 1  # current item id

        self.clean_pattern = r'<(.*)=(.*),(.*)'  # pattern to help clean tags strings that containing item links
        self.pattern_img = r'src=\"(.*)\"\s'  # pattern to find links in tags
        self.pattern = 'div class=\"photoarea photoarea-active\"'  # pattern to find divs with image links
        self.link_pattern = '<a href='  # pattern to find item's link

        self.output_directory = None
        self.categories = None
        self.delay_range_s = []
        self.max_retries = None
        self.headers = None
        self.restart = None
        self.logs_dir = None

    def get_html(self):
        """
        GETs url, retries connection if needed.
        :return:
        """
        try:
            self.response = requests.get(self.link)
            self.soup = BS(self.response.text, "html.parser")
            print('response received')
            Parser.item_url_setter(self)
        except Exception as e:
            print(e)
            Parser.retry(self)

    def page_url_setter(self):
        """
        Parses the whole catalog, at the moment there 5935 items, which means 119 pages by 50 items.
        TODO: calculate amount of pages
        :return:
        """
        if self.page <= 119:  # 119 is amount of pages atm
            self.link = 'https://zootovary.ru/catalog/?pc=50&PAGEN_1=' + str(self.page)
            self.page += 1
            Parser.get_html(self)

    def item_url_setter(self):
        self.body = str(self.soup.find_all())
        print(f'processing page {self.page}, item {self.item}')
        self.item += 1  # id of the item
        # TODO: check if item already exists
        # TODO: find link and save it to self.link
        # TODO: refactor func as a property of the Parser
        Parser.get_item_info(self)

    def get_image_link(self):
        """
        Gets link of the preview image.
        TODO: get all images
        :return:
        """
        # at first, get indexes of required div classes
        try:
            indexes = [i for i in range(len(self.body)) if self.body.startswith(self.pattern, i)]
            classes = []
            for i in indexes:
                classes.append(self.body[i + 47:i + 750])  # takes string with extend to not lose anything important

            classes = [i for i in classes if i.startswith(self.link_pattern)]  # find links
            tag = re.findall(self.clean_pattern, classes[0])
            tag = str(tag[0])
            # link of the preview image
            self.image_link = 'https://zootovary.ru' + ''.join(re.findall(self.pattern_img, tag))
        except Exception as e:
            print(e)
            self.image_link = None

    def get_item_info(self):
        """
        Runs all parsing funcs one by one.
        :return:
        """
        list_of_funcs = [Parser.item_url_setter, Parser.get_image_link]  # TODO: add parsing funcs, list comprehension?
        for func in list_of_funcs:
            try:
                yield func()
            except Exception as e:
                # proceed the next func if a func returns mistake
                print(e)
                print('Continue gathering info...')
                next(Parser.get_item_info(self))

    def save_to_csv(self):
        """
        Takes today's YearMonthDay, appends all the gathered info to lists, saves to file
        :return:
        """
        name = 'data' + str(datetime.date.today()[:8])  # data20220823
        fields = []
        rows = []
        # TODO: add gathered info to lists
        with open(name, 'w') as f:
            write = csv.writer(f)
            write.writerow(fields)
            write.writerows(rows)
            # TODO: maybe writing after each page and clearing lists will save memory?

    def get_item_category(self) -> int:
        # TODO: get category func
        ...

    def get_time(self) -> str:
        # TODO: get time of parsing a particular item
        ...

    def get_item_price(self) -> float:
        # TODO: get price of the item, both default and event price
        ...

    def get_sku_status(self) -> bool:
        # TODO: get availability of the item
        ...

    def get_sku_barcode(self) -> int:
        # TODO: get barcode of the item
        ...

    def get_sku_article(self) -> str:
        # TODO: get article of the item
        ...

    def get_sku_name(self) -> str:
        # TODO: get name of the item
        ...

    def get_sku_category(self) -> str:
        # TODO: get category of the item
        ...

    def get_sku_country(self) -> str:
        # TODO: get category of the item
        ...

    # TODO: get_sku_country - страна
    # TODO: sku_weight_min - вес
    # TODO: sku_volume_min - объем
    # TODO: sku_quantity_min - количество единиц, например, 100 салфеток в пачке

    def retry(self):
        self.max_retries = 3
        print('Connection error, retrying...')
        while self.max_retries > 0:
            time.sleep(3)  # imitate delay TODO: delay range randint
            self.max_retries -= 1
            Parser.get_html(self)

    def config(self):
        """
        Checks for config file and asks for settings if config not yet exists.
        :return:
        """
        path = input('Enter path to the config file')
        if os.path.exists(path):
            import json  # TODO: move import to the outer scope?
            import path  # needed
            self.output_directory = path.output_directory
            self.categories = path.categories
            self.delay_range_s = path.delay_range_s
            self.max_retries = path.max_retries
            self.headers = path.headers
            self.logs_dir = path.logs_dir
            self.restart = path.restart
            print(f'Config loaded from {path}')
        else:
            check = input('Would you like to setup settings? y\\n\n')
            if check.lower() != 'n':
                ...  # TODO: setup checks and defaults


def log_it():
    """
    Logs events and saves to the file.
    :return:
    """
    logger = logging.getLogger(__name__)
    logname = 'log' + str(datetime.date.today())
    logging.basicConfig(filename=logname,
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
    logger.error('Starting parser')


def main():
    log_it()
    Parser().config()
    Parser().get_html()


if __name__ == '__main__':  # doesn't work on Apache
    main()
