# coding:utf-8

import os
import sys
import argparse
import logging

import subCrawler


logging.basicConfig(level=logging.DEBUG)

def main():
    parser = argparse.ArgumentParser(description="migration manager")
    parser.add_argument("--module", "-m", type=str, required=True)
    args = parser.parse_args()

    module = args.module


if __name__ == "__main__":
    sys.exit(main())
