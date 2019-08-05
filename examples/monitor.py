# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com

import importlib
from os import path
from glob import glob
from utils import load_hist_iter
from utils import config


curdir = path.dirname(path.abspath(__file__))
pos_lst = config["pos_lst"]
buy_lst = []
sell_lst = []

stg_file_lst = glob("strategy/*py")
stg_cls_lst = []


def load_strategy():
    """倒入策略目录的所有策略"""
    for fname in stg_file_lst:
        if fname.startswith("__"):
            continue
        mod_name = fname.replace(path.sep, ".")[:-3]
        try:
            mod = importlib.import_module(mod_name)
            stg = getattr(mod, "Strategy")
            stg_cls_lst.append(stg)
        except Exception:
            continue


if __name__ == "__main__":
    for code, hist in load_hist_iter():
        for stg_cls in stg_cls_lst:
            stg = stg_cls()
            ret = stg.on_data(code, hist, pos_lst)

            if ret:
                buy_lst.extend(ret["buy_lst"])
                sell_lst.extend(ret["buy_lst"])
