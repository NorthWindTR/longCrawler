# coding:utf-8

import os
import sys
import json
import urllib
import time
import datetime
import jsonpath

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class GoogleSpider(object):

    def __init__(self):
        self.headers = {
            'authority': 'trends.google.com',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh_CN,zh;q=0.9',
        }

    @staticmethod
    def invoke(invoker):
        return invoker()

    def get(self, url, headers):
        print "crawl url:{}, headers:{}".format(url, headers)
        res = GoogleSpider.invoke(lambda: requests.get(url, headers=self.headers))
        return res


class GoogleTrendsToken1Spider(GoogleSpider):
    base_url = "https://trends.google.com/trends/explore"

    def retrieve_cookie(self, keyword):
        params = {
            "geo": "US",
            "q": keyword
        }

        res = self.get(
            url=GoogleTrendsToken1Spider.base_url + "?" + urllib.urlencode(params),
            headers=self.headers,
        )
        token = res.headers['Set-Cookie'].split(';')[0]
        return token


class GoogleTrendsToken2Spider(GoogleSpider):
    base_url = "https://trends.google.com/trends/api/explore"

    def retrieve_token(self, keyword, token1):
        params = {
            'hl': 'zh-CN',
            'tz': '-480',
            'req': json.dumps({
                "comparisonItem": [
                    {
                        "keyword": keyword,
                        "geo": "US",
                        "time": "today+12-m"
                    }
                ],
                "category": 0,
                "property": ""
            }),
        }

        query_string = "&".join(map(lambda (key, value): key + "=" + value, params.items()))

        self.headers.update({"cookie": token1})
        res = self.get(
            url=GoogleTrendsToken2Spider.base_url + "?" + query_string,
            headers=self.headers,
        )

        root = json.loads(res.content.split('\n')[1])
        token = root["widgets"][0]["token"]

        print "token2 retrieve:{}".format(token)
        return token


class GoogleTrendsSpider(GoogleTrendsToken1Spider, GoogleTrendsToken2Spider):
    base_url = "https://trends.google.com/trends/api/widgetdata/multiline/csv"

    def __init__(self, keyword):
        super(GoogleTrendsSpider, self).__init__()
        self.keyword = keyword
        print "start to crawl google trends keyword:{}".format(keyword)

    def run(self):
        cookie = self.retrieve_cookie(self.keyword)
        token = self.retrieve_token(self.keyword, cookie)

        return self.crawl(token, self.keyword)

    def crawl(self, token2, keyword):
        today = datetime.date.today()
        last_year = today - datetime.timedelta(days=365)

        params = {
            'req': json.dumps({
                "time": "{} {}".format(last_year.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")),
                "resolution": "WEEK",
                "locale": "zh-CN",
                "comparisonItem": [
                    {
                        "geo": {
                            "country": "US"
                        },
                        "complexKeywordsRestriction": {
                            "keyword": [
                                {
                                    "type": "BROAD",
                                    "value": keyword
                                }
                            ]
                        }
                    }
                ],
                "requestOptions": {
                    "property": "",
                    "backend": "IZG",
                    "category": 0
                }
            }),
            'token': token2,
            'tz': '0'
        }

        res = self.get(
            url=GoogleTrendsSpider.base_url + "?" + urllib.urlencode(params),
            headers=self.headers,
        )
        return res.content


if __name__ == "__main__":
    print GoogleTrendsSpider("Cleaning Kits").run()
    print GoogleTrendsSpider("Putty").run()

