# coding:utf-8

import os
import sys
import requests


class Crawler(object):
    Headers = {
        "authority": "www.amazon.com",
        'cache-control': 'max-age=0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
        'sec-ch-ua-mobile': '?0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-US,en;q=0.9'
    }

    @staticmethod
    def crawl(url):
        try:
            res = requests.get(url, headers=Crawler.Headers, verify=False)
            if res.status_code / 100 != 2:
                print "fetch {} fail, return code:{}, msg:{}".format(url, res.status_code, res.content)
            return res.content
        except Exception as e:
            print "crawl:{} fail".format(url)
        return ""
