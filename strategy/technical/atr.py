# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com

import pandas as pd


def atr_calc(df, n=14):
    data = pd.DataFrame()
    high = df["high"]
    low = df["low"]
    close = df["close"]
    data['tr0'] = abs(high - low)
    data['tr1'] = abs(high - close.shift())
    data['tr2'] = abs(low - close.shift())
    tr = data[['tr0', 'tr1', 'tr2']].max(axis=1)
    atr = tr.rolling(10).mean()
    df["atr"] = atr
    return df
