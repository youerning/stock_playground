# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
import sqlite3
import logging
import os
import sys
import pandas as pd
from glob import glob
from os import path
from settings import config
from datetime import datetime


READALL_SQL = "SELECT * FROM DATA"
READ_ONE_SQL = "SELECT * FROM DATA ORDER BY trade_date DESC LIMIT 1"
data_path_name = "data"
curdir = path.dirname(path.abspath(__file__))
data_path = path.join(curdir, data_path_name)


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


def load_hist(ts_code=None, start_date=None, end_date=None, func=None):
    """加载本地历史数据

    func: 用于过滤历史数据的函数, 接受一个Datarame对象
    start_date: 起始时间
    end_date: 截至时间
    """
    db_glob_lst = glob(path.join(data_path, "*.csv"))
    for fp in db_glob_lst:
        if ts_code and ts_code in fp:
            hist = pd.read_csv(fp, parse_dates=["trade_date"], index_col="trade_date")
            code = hist.ts_code[0]
            yield code, hist
            return
        else:
            continue
        hist = pd.read_csv(fp, parse_dates=["trade_date"], index_col="trade_date")
        if func is not None:
            hist = func(hist)
        code = hist.ts_code[0]
        yield code, hist


def load_all_hist():
    """load_hist的快捷方法"""
    data = {code: hist for code, hist in load_hist()}
    return data


def convert():
    """convert data store with format sqlite to data with format csv"""
    db_glob_lst = glob(path.join(data_path, "*.db"))
    for db_path in db_glob_lst:
        fp = db_path[:-3] + ".csv"
        if path.exists(fp):
            continue

        with sqlite3.connect(db_path) as conn:
            data = pd.read_sql(READALL_SQL, conn, parse_dates=["trade_date"])
            data.sort_values("trade_date").to_csv(fp, index=False)

    db_glob_lst = glob(path.join(data_path, "*.csv"))
    for db_path in db_glob_lst:
        data = pd.read_csv(db_path, parse_dates=["trade_date"])
        data.sort_values("trade_date").to_csv(db_path, index=False)


def es_client():
    from elasticsearch import Elasticsearch
    es = Elasticsearch(config["es_host"])

    return es


def find_max_date(ts_code, index_name):
    es = es_client()
    body = {
        "aggs": {
            "trade_date": {
                "max": {
                    "field": "trade_date"
                }
            }
        },
        "size": 0,
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            "ts_code.keyword": {
                                "query": ts_code
                            }
                        }
                    }
                ]
            }
        }
    }

    try:
        ret = es.search(body=body, index=index_name)
    except Exception:
        return None

    return ret["aggregations"]["trade_date"]["value"]


def dump():
    from elasticsearch.helpers import bulk
    date_format = "%Y-%m-%dT%H:%M:%S.%f+0800"
    es = es_client()
    # print(es.search())
    index_name = config["stock_index_name"]
    hist_data = load_hist()

    for code in hist_data:
        print("开始上传股票: %s" % code)
        data = hist_data[code]

        bulk_lst = []
        max_date = find_max_date(code, index_name)
        if max_date:
            max_date = datetime.fromtimestamp(max_date / 1000)
            data = data[data.trade_date > max_date]

        for idx, value in enumerate(data.values, start=1):
            doc = {}
            for col_name, v in zip(data.columns, value):
                doc[col_name] = v

            if doc["trade_date"] > max_date:
                continue
            doc["trade_date"] = doc["trade_date"].strftime(date_format)
            doc_id = "-".join([doc["ts_code"], doc["trade_date"]])
            bulk_lst.append({
                            "_index": index_name,
                            "_id": doc_id,
                            "_type": "doc",
                            "_source": doc,
                            })

            if idx % 500 == 0:
                bulk(es, bulk_lst, stats_only=True)
                bulk_lst = []

        if bulk_lst:
            bulk(es, bulk_lst, stats_only=True)


def dump_index():
    import tushare as ts
    from elasticsearch.helpers import bulk
    date_format = "%Y-%m-%dT%H:%M:%S.%f+0800"
    es = es_client()
    token = config["token"]
    index_name = config["index_index_name"]

    ts.set_token(token)
    data = ts.pro_bar(ts_code='000001.SH', asset='I', start_date=config["START_DATE"])
    data.trade_date = pd.to_datetime(data.trade_date)
    index_code = data.ts_code[0]

    bulk_lst = []
    max_date = find_max_date(index_code, index_name)
    if max_date:
        max_date = datetime.fromtimestamp(max_date / 1000)
        data = data[data.trade_date > max_date]

    for idx, value in enumerate(data.values, start=1):
        doc = {}
        for col_name, v in zip(data.columns, value):
            doc[col_name] = v

        doc["trade_date"] = doc["trade_date"].strftime(date_format)
        doc_id = "-".join([doc["ts_code"], doc["trade_date"]])
        bulk_lst.append({
                        "_index": index_name,
                        "_id": doc_id,
                        "_type": "doc",
                        "_source": doc,
                        })

        if idx % 500 == 0:
            print(bulk(es, bulk_lst, stats_only=True))
            bulk_lst = []

    if bulk_lst:
        print(bulk(es, bulk_lst, stats_only=True))


if __name__ == "__main__":
    print(find_max_date("000012.SZ", "stock"))
    print(find_max_date("000001.SH", "index"))
