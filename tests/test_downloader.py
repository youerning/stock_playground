# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
import pytest
import pandas as pd
from nobody.utils import get_ts_client
from nobody.downloader.ts_data import code_gen
from nobody.downloader.ts_data import save_data
from nobody.downloader.ts_data import download
from nobody.settings import config


class TestTsData(object):
    def setup(self):
        self.ts = get_ts_client()
        self.pro = self.ts.pro_api(config["ts_token"])
        self.code_lst = self.pro.stock_basic(list_status='L', fields='ts_code,symbol,name,area,industry,list_date').ts_code
        self.start_date = pd.to_datetime("2018-01-03")

    def test_code_gen(self):
        assert len(list(code_gen(self.code_lst))) == len(self.code_lst)

    def test_save_data(self, tmp_path):
        tmp_file = tmp_path / "tmp.csv"

        save_data("000001.SZ", self.start_date, open(tmp_file, "w"))
        print(open(tmp_file).read(20))
        df = pd.read_csv(open(tmp_file, "r"), parse_dates=["trade_date"], index_col="trade_date")

        assert df.index[0] == self.start_date

    @pytest.mark.skip(reason="not finished")
    def test_download(self):
        pass

