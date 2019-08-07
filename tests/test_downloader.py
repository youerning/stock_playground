# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
import pytest
from nobody.utils import get_ts_client
from nobody.downloader.ts_data import code_gen
from nobody.downloader.ts_data import save_data
from nobody.downloader.ts_data import download
from nobody.settings import config


class TestTsData(object):
    def setup(self):
        self.ts = get_ts_client()
        pro = ts.pro_api(config["ts_token"])
        self.code_lst = 

    print("开始下载...")
    data = pro.stock_basic(list_status='L', fields='ts_code,symbol,name,area,industry,list_date')

    def test_code_gen(self):
        pass