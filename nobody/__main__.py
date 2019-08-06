# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com

import argparse
from .downloader.ts_data import download
from .utils.es import dump
from .utils.es import dump_index


def initialize():
    print("init")


if __name__ == "__main__":
    action_lst = ["save_data", "dump", "dump_index", "init"]
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument('action', choices=action_lst)
    args = parser.parse_args()
    # convert()

    if args.action == "dump":
        dump()
    elif args.action == "dump_index":
        dump_index()
    elif args.action == "save_data":
        download()
    elif args.action == "init":
        initialize()
