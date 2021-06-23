# coding:utf-8

import os
import sys
import logging
import copy
import re
from Queue import Queue
from multiprocessing.dummy import Pool

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from lxml import etree

from crawler import Crawler

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Item(object):
    root_xpath = '//ul[@id="zg_browseRoot"]/ul/'

    level_xpath = 'ul/'

    def __init__(self, url, name, level, parent):
        self.name = name
        self.url = url
        self.level = level
        self.parent = parent

    def get_xpath(self):
        return Item.root_xpath + Item.level_xpath * self.level + 'li'


class AmazonBestSellers(Crawler):
    root_xpath = '//ul[@id="zg_browseRoot"]/ul/li'
    default_level = 0
    count = 0

    def __init__(self, base_url, base_categories):
        logging.info("amazon best sellers start")
        self.base_categories = base_categories
        self.base_url = base_url
        self.category_urls = set(self.base_url)
        self.result_items = set()
        self.queue = Queue()
        self.file = open("target.txt", 'w+')

    def browse_root(self, item):
        try:
            return self.browse_root_internal(item)
        except Exception as e:
            print "crawl item:{} fail, return null list".format(item.name)
        return list()

    def browse_root_internal(self, item):
        content = Crawler.crawl(item.url)
        selector = etree.HTML(content)

        result = list()
        for x in selector.xpath(item.get_xpath()):
            raw_url_items = x.xpath('a/@href')
            url = None
            if len(raw_url_items) > 0:
                url = AmazonBestSellers.cleanup_url(raw_url_items[0])

            category = AmazonBestSellers.cleanup_category_name(x.xpath('string(.)'))

            result.append(Item(url, category, item.level + 1, item.name))
        return result

    @staticmethod
    def cleanup_url(url):
        if url is not None:
            url = url.split('ref')[0]
        return url

    @staticmethod
    def cleanup_category_name(name):
        name = name.strip()
        return name

    def run(self):
        root_items = filter(
            lambda x: x.name in self.base_categories,
            self.browse_root(
                Item(self.base_url, "root", AmazonBestSellers.default_level, None)
            )
        )

        print "parse root browse complete:{}, start to crawl...".format(','.join(map(lambda x: x.name, root_items)))

        self.start(root_items)

    def start(self, items):
        self.crawl(items)

    def crawl(self, items):
        for item in items:
            if item.name in self.result_items:
                print "item:{} has been crawled...".format(item.name)

            if item.url is None:
                continue

            if item.url in self.category_urls:
                print "item:{} url:{} has been crawled".format(item.name, item.url)
                continue

            self.crawl_internal(item)

            self.result_items.update(item.name)

    def crawl_internal(self, item):
        sub_categories = self.browse_root(item)
        print "start to crawl number:{}, category:{}, level:{}, parent:{}, return:{}, url:{}" \
            .format(AmazonBestSellers.count, item.name.encode('utf-8'), item.level, item.parent.encode('utf-8'),
                    len(sub_categories), item.url)

        self.parse(item, sub_categories)
        self.crawl(sub_categories)

    def parse(self, item, sub_categories):
        self.category_urls.update(item.url)
        AmazonBestSellers.count += 1
        if len(sub_categories) == 0:
            self.file.write(item.name + "\n")

    def __del__(self):
        self.file.close()
        with open("result.txt", "w+") as fd:
            for item in self.result_items:
                fd.write(item + "\n")


def main():
    AmazonBestSellers(
        "https://www.amazon.com/Best-Sellers/zgbs/",
        {"Automotive"}
    ).run()


if __name__ == "__main__":
    sys.exit(main())
