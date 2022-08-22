import time

from bs4 import BeautifulSoup as BS
import requests
import re


# body = str(soup.find_all())
# print('response received')
# pattern = 'div class=\"photoarea photoarea-active\"'
# sec_pattern = '<a href='

# indexes = [i for i in range(len(body)) if body.startswith(pattern, i)]
# print('indexes acquired')
# classes = []
# for i in indexes:
#    classes.append(body[i + 47:i + 750])

# fixed_classes = [i for i in classes if i.startswith(sec_pattern)]


# tag = re.findall(clean_pattern, fixed_classes[0])
# tag = str(tag[0])
# image_link = 'https://zootovary.ru' + ''.join(re.findall(pattern_img, tag))
# print(tag)


class Parser:
    def __init__(self):
        self.retry = 0  # amount of retires, set by Parser().retry()
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

    def get_html(self):
        try:
            self.response = requests.get(self.link)
            self.soup = BS(self.response.text, "html.parser")
            print('response received')
            Parser.item_url_setter(self)
        except Exception as e:
            print(e)
            Parser.retry(self)

    def page_url_setter(self):
        if self.page <= 119:  # 119 is amount of pages atm, didn't have time to create calculation func
            self.link = 'https://zootovary.ru/catalog/?pc=50&PAGEN_1=' + str(self.page)
            self.page += 1
            Parser.get_html(self)

    def item_url_setter(self):
        self.body = str(self.soup.find_all())
        print(f'processing page {self.page}, item {self.item}')
        self.item += 1
        Parser.gather_item_info(self)

    def get_image_link(self):

        indexes = [i for i in range(len(self.body)) if self.body.startswith(self.pattern, i)]

        classes = []
        for i in indexes:
            classes.append(self.body[i + 47:i + 750])

        classes = [i for i in classes if i.startswith(self.link_pattern)]
        tag = re.findall(self.clean_pattern, classes[0])
        tag = str(tag[0])
        self.image_link = 'https://zootovary.ru' + ''.join(re.findall(self.pattern_img, tag))

    def get_item_link(self):
        self.body = str(self.soup.find_all())
        indexes = [i for i in range(len(self.body)) if self.body.startswith(self.pattern, i)]
        print(f'processing page {self.page}')

        classes = []
        for i in indexes:
            classes.append(self.body[i + 47:i + 750])

        classes = [i for i in classes if i.startswith(self.link_pattern)]
        tag = re.findall(self.clean_pattern, classes[0])
        tag = str(tag[0])
        self.item_link = 'https://zootovary.ru' + ''.join(re.findall(self.pattern_img, tag))

    def gather_item_info(self):
        Parser.get_item_link(self)
        Parser.get_image_link(self)

    def retry(self):
        self.retry = 3
        print('Connection error, retrying...')
        while self.retry > 0:
            time.sleep(3)
            self.retry -= 1
            Parser.get_html(self)


print(Parser().page_url_setter())
