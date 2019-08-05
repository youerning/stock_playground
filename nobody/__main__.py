# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com

import argparse
from .utils.save_data import main as save_data
from .utils.utils import convert
from .utils.utils import dump
from .utils.utils import dump_index


def initialize():
    print("init")


if __name__ == "__main__":
    action_lst = ["save_data", "convert", "dump", "dump_index", "init"]
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument('action', choices=action_lst)
    args = parser.parse_args()
    # convert()

    if args.action == "convert":
        convert()
    elif args.action == "dump":
        dump()
    elif args.action == "dump_index":
        dump_index()
    elif args.action == "save_data":
        save_data()
    elif args.action == "init":
        initialize()
