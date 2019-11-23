# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com


class K(object):
    """用于寻找长实体(cst), 十字星(szx), 长影线(cyx), 吞噬(ts), 窗口(ck), 包孕(by)等形态"""

    def find(self, df, name, **kwargs):
        """
        发现指定的K线形态

        Parameters
        ---------
        df: pd.DataFrame
            时间序列为index, 并且包含open, high, low, close, voloume字段名的DataFrame对象
        name:str or function
            k线形态名称, 可用形态: 长实体(cst), 十字星(szx), 长影线(cyx), 吞噬(ts), 包孕(by), 窗口(ck)
            也可以传入一个接受df为参数的函数
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

    @staticmethod
    def get_shape(bar):
        """
        获取单个k线的基本信息，如上影线高度，下影线高度，实体高度(正值表明上涨，反之下跌)

        Parameters
        ---------
        bar: pandas.core.series.Series
            时间序列为index, 并且包含open, high, low, close, voloume字段名的Series对象
        Returns
        ---------
        tuple
            (浮动数值, 上影线长度, 下影线长度, 实体长度)
        """
        # height 实体的长度
        # ulh upper line height, 上影线的高度
        # llh lower line height, 下影线的高度

        entity = (bar.close - bar.open) / bar.open
        # 虽然代码行数多了四行，但是open, close只需要比较一次
        if bar.open > bar.close:
            ulh = (bar.high - bar.open) / bar.open
            llh = (bar.low - bar.close) / bar.close
        else:
            ulh = (bar.high - bar.close) / bar.close
            llh = (bar.low - bar.open) / bar.open
        # ulh = bar.high - max([bar.open, bar.close])
        # llh = min([bar.open, bar.close]) - bar.low

        return entity, ulh, llh

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
        pass

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
        pass

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
        pass

    def djx(self, df, ulh=0.005, llh=0.025, entity_max=0.02, entity_min=0.005, status="white"):
        """
        寻找吊颈线形态

        Parameters
        ---------
        df: pd.DataFrame
            时间序列为index, 并且包含open, high, low, close, voloume字段名的DataFrame对象

        lh: float
            吊颈线的线长百分比
        entity: float
            实体的长度的百分比
        status: str
            吊颈线的状态, black代表阴线，white代表阳线, 默认为阴线

        Returns
        ---------
        list
          包含pandas.Timestamp对象的列表, 时间戳对象指向形态的时间发生位置
        """
        choices = {"black": -1, "white": 1}
        if status not in choices:
            raise ValueError("status参数错误")

        res = []
        for idx, bar in df.iterrows():
            bar_entity, bar_ulh, bar_llh = K.get_shape(bar)
            cond = [bar_entity >= entity_min, bar_entity <= entity_max, bar_ulh <= ulh, abs(bar_llh) >= llh]
            if all(cond):
                res.append(idx)

        return res

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
        pass

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
        pass

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
        pass

