# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
import pandas as pd
from glob import glob
from nobody.utils.utils import load_hist
from nobody.settings import config
from os import path


class TestUtils(object):
    def setup(self):
        self.start_date = "2018-01-02"
        self.end_date = "2019-01-02"

    def test_load_hist(self):
        assert len(list(load_hist("000001.SZ"))) == 1
        assert len(list(load_hist(["000001.SZ", "000002.SZ"]))) == 2
        assert len(list(load_hist())) == len(glob(path.join(config["STOCK_DATA_DIR"], "*csv")))

        data = list(load_hist("000001.SZ", start_date=self.start_date, end_date=self.end_date))
        hist = data[0][1]

        assert pd.to_datetime(self.start_date) == hist.index[0]
        assert pd.to_datetime(self.end_date) == hist.index[-1]
