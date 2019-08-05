# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com

import json
from os import path


config_file_name = "config.json"
curdir = path.dirname(path.abspath(__file__))
# config_path = path.join(curdir, config_file_name)
config = json.load(open(config_file_name))

# es 配置
config["es_host"] = ["192.168.56.102:9200"]
# 股票索引名称
config["stock_index_name"] = 'stock'
# 指数索引名称
config["index_index_name"] = "index"


# 数据保存配置
config["START_DATE"] = "2012-01-01"
config["DATA_DIR"] = "data"
config["DAY_FORMAT"] = "%Y%m%d"
config["MAX_TRY"] = 5
# (24 + 17) * 60 * 60
# 服务端每天 15-17更新时间
config["UPDATE_INTERVAL"] = 41 * 60 * 60
