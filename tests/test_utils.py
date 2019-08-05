# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
from nobody.utils.utils import load_hist
from nobody.utils.utils import load_all_hist
from nobody.utils.utils import dump
from nobody.utils.utils import dump_index


class TestUtils(object):
    def test_load_hist(self):
        feed = {}
        for code, hist in load_hist("000002.SZ"):
            feed[code] = hist

        assert len(feed) > 1

    def test_load_all_hist(self):
        pass

    def test_dump(self):
        pass

    def test_dump_index(self):
        pass
