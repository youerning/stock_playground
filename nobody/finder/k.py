# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com


class K(object):
    """用于寻找长实体(cst), 十字星(szx), 长影线(cyx), 吞噬(ts), 窗口(ck), 包孕(by)等形态"""

    def find(self, df, name, **kwargs):
        """
        发现指定的k线形态

        Parameters
        ---------
        df: pd.DataFrame
            时间序列为index, 并且包含open, high, low, close, voloume字段名的DataFrame对象
        name:str
            k线形态名称, 可用形态长实体(cst), 十字星(szx), 长影线(cyx), 吞噬(ts), 包孕(by), 窗口(ck)
        `**kwds` : keywords
            传递给调用方法的关键字参数


        Returns
        ---------
        list
            包含pandas.Timestamp对象的列表, 时间戳对象指向形态的时间发生位置

        Raises
        ------
        AttributeError
            当找不到相应的方法
        """
        func = getattr(self, name)
        return func(df, **kwargs)

    def common(self, df, height, ulh, llh):
        """
        识别单根k线的形态的通用接口

        Parameters
        ---------
        df: pd.DataFrame
            时间序列为index, 并且包含open, high, low, close, voloume字段名的DataFrame对象
        height: float
            实体的长度, 默认是最高与最低的距离是5%或以上
        ulh: float
            upper line height, 上影线的高度
        llh: float
            lower line height, 下影线的高度

        Returns
        ---------
        list
            包含pandas.Timestamp对象的列表, 时间戳对象指向形态的时间发生位置
        """

        pass

    def cst(self, df, height=5, lh=0.1):
        """
        寻找长实体形态

        Parameters
        ---------
        df: pd.DataFrame
            时间序列为index, 并且包含open, high, low, close, voloume字段名的DataFrame对象
        height: float
            长实体的长度, 默认是最高与最低的距离是5%或以上
        lh: float
            上影线或下影线的高度，默认是涨幅度的0.2

        Returns
        ---------
        list
            包含pandas.Timestamp对象的列表, 时间戳对象指向形态的时间发生位置
        """

    def szx(self, df):
        """
        寻找十字星形态

        Parameters
        ---------
        df: pd.DataFrame
            时间序列为index, 并且包含open, high, low, close, voloume字段名的DataFrame对象

        Returns
        ---------
        list
          包含pandas.Timestamp对象的列表, 时间戳对象指向形态的时间发生位置
        """

    def cyx(self, df):
        """
        寻找长影线形态

        Parameters
        ---------
        df: pd.DataFrame
            时间序列为index, 并且包含open, high, low, close, voloume字段名的DataFrame对象

        Returns
        ---------
        list
          包含pandas.Timestamp对象的列表, 时间戳对象指向形态的时间发生位置
        """

    def ts(self, df):
        """
        寻找吞噬形态

        Parameters
        ---------
        df: pd.DataFrame
            时间序列为index, 并且包含open, high, low, close, voloume字段名的DataFrame对象

        Returns
        ---------
        list
          包含pandas.Timestamp对象的列表, 时间戳对象指向形态的时间发生位置
        """

    def by(self, df):
        """
        寻找包孕形态

        Parameters
        ---------
        df: pd.DataFrame
            时间序列为index, 并且包含open, high, low, close, voloume字段名的DataFrame对象

        Returns
        ---------
        list
          包含pandas.Timestamp对象的列表, 时间戳对象指向形态的时间发生位置
        """

    def ck(self, df):
        """
        寻找跳空窗口

        Parameters
        ---------
        df: pd.DataFrame
            时间序列为index, 并且包含open, high, low, close, voloume字段名的DataFrame对象

        Returns
        ---------
        list
          包含pandas.Timestamp对象的列表, 时间戳对象指向形态的时间发生位置
        """

