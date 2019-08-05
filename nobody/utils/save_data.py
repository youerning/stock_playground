# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com

# 下载日线数据
import tushare as ts
import pandas as pd
import time
import os
from datetime import datetime
from datetime import timedelta
from os import path
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures as futures
from ..settings import config


curdir = path.dirname(path.abspath(__file__))
# 方便直接调用
START_DATE = config["START_DATE"]
# END_DATE = ""
DATA_DIR = config["DATA_DIR"]
DAY_FORMAT = config["DAY_FORMAT"]
MAX_TRY = config["MAX_TRY"]
# (24 + 17) * 60 * 60
UPDATE_INTERVAL = config["UPDATE_INTERVAL"]
pass_set = set()


def code_gen(code_lst):
    """
    generate code, start_date, fp

    code: str
    start_date: str
    fp: str, file path
    """
    global pass_set
    # 查询当前所有正常上市交易的股票列表
    data_path = DATA_DIR

    if not path.exists(data_path):
        os.mkdir(data_path)

    now = datetime.now()
    oneday = timedelta(days=1)

    for code in code_lst:
        if code in pass_set:
            continue

        fp = path.join(data_path, "%s.csv" % code)

        if path.exists(fp):
            df = pd.read_csv(fp, parse_dates=["trade_date"])
            latest_trade_date = max(df["trade_date"])

            date_diff = now - latest_trade_date

            if date_diff.total_seconds() > UPDATE_INTERVAL:
                start_date = latest_trade_date + oneday
                start_date = start_date.strftime(DAY_FORMAT)
                # print(start_date)
                yield code, start_date, fp
            else:
                pass_set.add(code)
        else:
            yield code, START_DATE, fp


def save_data(code, start_date, fp):
    print("下载股票(%s)日线数据到 %s" % (code, fp))

    try:
        data = ts.pro_bar(ts_code=code, adj='qfq', start_date=start_date)
        # 当超过调用次数限制返回None
        if data is None:
            time.sleep(10)
            return
        pass_set.add(code)
    except Exception:
        time.sleep(10)
        print("股票: %s 下载失败" % code)
        return

    if len(data) == 0:
        pass_set.add(code)
        return

    try:
        data.trade_date = pd.to_datetime(data.trade_date)
        data = data.sort_values("trade_date")
        if path.exists(fp):
            data.to_csv(fp, mode="a", header=False, index=False)
        else:
            data.to_csv(fp, index=False)
    except Exception:
        print("股票:%s 保存失败" % code)


def main():
    future_lst = []
    pool = ThreadPoolExecutor(3)
    token = config["token"]
    ts.set_token(token)
    pro = ts.pro_api(token)

    print("开始下载...")
    data = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    code_lst = data.ts_code
    # print(code_lst)

    for i in range(1, MAX_TRY + 1):
        for code, start_date, fp in code_gen(code_lst):
            future = pool.submit(save_data, code, start_date, fp)
            future_lst.append(future)

        futures.wait(future_lst)
        if len(pass_set) == len(code_lst):
            break
        print("第%s次任务完成" % i)

    print("所有任务完成, 总共尝试了%s次" % i)


if __name__ == '__main__':
    main()
