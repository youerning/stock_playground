# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com

import sys
import yaml
import os
from os import path

config = {}

# 默认配置
# es 配置
config["ES_HOST"] = ["192.168.56.102:9200"]
# 股票索引名称
config["STOCK_INDEX_NAME"] = 'stock'
# 指数索引名称
config["INDEX_INDEX_NAME"] = "index"


# 数据保存配置
config["START_DATE"] = "2012-01-01"
# 数据目录
config["DATA_DIR"] = "data"
# 股票历史数据保存目录
config["STOCK_DATA_DIR"] = "data/stock"
# 股票指数历史数据保存目录
config["INDEX_DATA_DIR"] = "data/index"
config["DAY_FORMAT"] = "%Y%m%d"
config["MAX_TRY"] = 5
# (24 + 17) * 60 * 60
# 服务端每天 15-17更新时间
config["UPDATE_INTERVAL"] = 41 * 60 * 60

if path.exists("config.yml"):
    with open("config.yml", encoding="utf8") as rf:
        user_config = yaml.safe_load(rf)
        config.update(user_config)
else:
    sys.exit("必须在当前目录下配置config.yml")

if not path.exists(config["STOCK_DATA_DIR"]):
    os.mkdir(config["STOCK_DATA_DIR"])

if not path.exists(config["INDEX_DATA_DIR"]):
    os.mkdir(config["INDEX_DATA_DIR"])
