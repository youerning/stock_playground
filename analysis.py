# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
import json
import argparse
import os
import tushare as ts
import pandas as pd
from os import path
from datetime import datetime


RESULT_PATH_NAME = "result"
DAY_FORMAT = "%Y%m%d"
START_DATE = "2012-01-01"
curdir = path.dirname(path.abspath(__file__))
config_file_name = "config.json"
config_path = path.join(curdir, config_file_name)
config = json.load(open(config_path))
# get
pro = ts.pro_api(config_path["token"])


def atr_calc(df, n=14):
    data = pd.DataFrame()
    high = df["high"]
    low = df["low"]
    close = df["close"]
    data['tr0'] = abs(high - low)
    data['tr1'] = abs(high - close.shift())
    data['tr2'] = abs(low - close.shift())
    tr = data[['tr0', 'tr1', 'tr2']].max(axis=1)
    atr = tr.rolling(10).mean()
    df["atr"] = atr
    return df


def ma_calc(df, ma_lst=(5, 10, 20)):
    for ma in ma_lst:
        col_name = "ma%s" % ma
        df[col_name] = df.rolling(ma).mean()

    return ma_calc


def risk_preprocess(df, period):
    df = df.sort_values("trade_date")
    df.trade_date = pd.to_datetime(df.trade_date)
    df.index = df.trade_date

    df = ma_calc(df)
    df["std"] = df.close.rolling(period).std()
    df = atr_calc(df)

    return df


def market():
    """探测市场温度"""
    pass


def risk_plot(df, index_df):
    """
    图片排布
    指数趋势图(close)
    指数risk趋势图
    股票ma趋势图
    股票risk趋势图

    ma趋势图:
        1. close趋势线
        2. ma趋势线

    risk趋势图:
        1. 趋势线 std, atr
        2. 画出一个月内最高价，最低价直线，并标明价格(指数不用)

    """
    from matplotlib import style
    style.use('ggplot')

    fig = plt.figure()
    ax1 = fig.add_subplot(411)
    ax2 = fig.add_subplot(412)
    ax3 = fig.add_subplot(413)
    ax4 = fig.add_subplot(414)

    result_path = path.join(curdir, RESULT_PATH_NAME)
    if not path.exists(result_path):
        os.mkdir(result_path)

    fname = "%s.png" % df.ts_code[0]
    save_path = path.join(result_path, fname)


def main():
    now = datetime.now()
    now_str = now.strftime(DAY_FORMAT)
    code_lst = config["code_lst"]

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="count", default=0)
    parser.add_argument("-s", "--start", default=START_DATE)
    parser.add_argument("-e", "--end", default=now_str)
    args = parser.parse_args()

    data = {}
    for code in code_lst:
        pass

    sh_index = pro.index_daily(ts_code="000001.SH", start_date=args.start, end_date=args.end)
