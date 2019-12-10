# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
import logging
import os
import sys
import numpy as np
import pandas as pd
import tushare as ts
from glob import glob
from os import path
from ..settings import config


# data_path = config["STOCK_DATA_PATH"]


def init_log(name, level=30, log_to_file=False):
    logger = logging.getLogger(name)
    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_to_file:
        if sys.platform.startswith("linux"):
            fp = "/var/log/%s.log" % name
        else:
            fp = path.join(os.environ["HOMEPATH"], "%s.log" % name)

        file_handler = logging.FileHandler(filename=fp)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
    return logger


def read_csv(fp):
    """读取通过tushare保存的csv文件

    Parameters:
    ----------
      fp:str
            csv文件路径

    Returns
    -------
    pandas.core.frame.DataFrame
    """
    hist = pd.read_csv(fp, parse_dates=["trade_date"], index_col="trade_date")

    return hist


def load_from_path(fp_lst, code=None, start_date=None, end_date=None, func=None,):
    """加载文件列表的股票数据

    Parameters:
        code: str or list
                单个或者多个股票代码的列表
        fp_lst: list
                数据文件列表
        start_date: str
                起始时间字符串, 比如2018-01-01
        end_date: str
                截至时间字符串, 比如2019-01-01
        func: function
                用于过滤历史数据的函数, 接受一个Datarame对象, 并返回过滤的DataFrame对象
    """
    for fp in fp_lst:
        fp_code = path.basename(fp)[:-4]
        if code:
            if fp_code == code:
                hist = pd.read_csv(fp)
            else:
                continue
        else:
            hist = pd.read_csv(fp)

        if func:
            hist = func(hist)

        # if start_date:
        #     start_date = pd.to_datetime(start_date)
        #     hist = hist[hist.index >= start_date]

        # if end_date:
        #     end_date = pd.to_datetime(end_date)
        #     hist = hist[hist.index <= end_date]
        yield fp_code, hist


def load_hist(ts_code=None, start_date=None, end_date=None, func=None, random=True, typ="tdx"):
    """加载本地历史数据

    Parameters:
        ts_code: str or list
                单个或者多个股票代码的列表
        start_date: str
                起始时间字符串, 比如2018-01-01
        end_date: str
                截至时间字符串, 比如2019-01-01
        func: function
                用于过滤历史数据的函数, 接受一个Datarame对象, 并返回过滤的DataFrame对象
        random: bool
                是否打乱加载的股票顺序, 默认为True
    """

    db_glob_lst = glob(path.join(data_path, "*.csv"))
    if len(db_glob_lst) == 0:
        print("当前数据目录没有任何历史数据文件")
        return

    if random:
        np.random.shuffle(db_glob_lst)

    for fp in db_glob_lst:
        fp_ts_code = path.basename(fp)[:-4]
        if ts_code:
            if fp_ts_code in ts_code:
                hist = pd.read_csv(fp, parse_dates=["trade_date"], index_col="trade_date")
                code = hist.ts_code[0]
            else:
                continue
        else:
            hist = pd.read_csv(fp, parse_dates=["trade_date"], index_col="trade_date")
            code = hist.ts_code[0]

        if func:
            hist = func(hist)

        if start_date:
            start_date = pd.to_datetime(start_date)
            hist = hist[hist.index >= start_date]

        if end_date:
            end_date = pd.to_datetime(end_date)
            hist = hist[hist.index <= end_date]

        yield code, hist


def load_hs300_hist():
    pass


def load_all_hist():
    """加载所有历史数据, load_hist的快捷方法"""
    data = {code: hist for code, hist in load_hist()}
    return data


def load_n_hist(n):
    """获取指定数量的历史数据"""
    data = {}
    c = 0
    for code, hist in load_hist():
        c += 1
        data[code] = hist
        if c >= n:
            break
    return data


def get_ts_client():
    ts.set_token(config["TS_TOKEN"])

    return ts


def get_pro_client():
    ts.set_token(config["TS_TOKEN"])

    return ts
