# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
import pandas as pd
from datetime import datetime
from .utils import load_hist
from ..settings import config


def es_client():
    from elasticsearch import Elasticsearch
    es = Elasticsearch(config["ES_HOST"])

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
    index_name = config["STOCK_INDEX_NAME"]
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
    index_name = config["INDEX_INDEX_NAME"]

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
