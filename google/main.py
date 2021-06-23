# coding:utf-8

import os
import sys
import argparse
import traceback

from google_trends import GoogleTrendsSpider


class GoogleTrendsSpiderWrapper(object):
    def __init__(self, filename):
        self.filename = filename
        self.fd = open(self.filename, "r+")
        self.words = map(lambda x: x.strip(), self.fd.readlines())

    def run(self):
        for keyword in self.words:
            try:
                content = GoogleTrendsSpider(keyword).run()
                with open("result/" + keyword + ".txt", "w+") as fd:
                    fd.write(content)
            except Exception as e:
                pass


def main():
    parser = argparse.ArgumentParser(description="google trends spider")
    parser.add_argument("--file", "-m", type=str, required=True)
    args = parser.parse_args()

    filename = args.file

    spider = GoogleTrendsSpiderWrapper(filename)
    spider.run()


if __name__ == "__main__":
    sys.exit(main())
