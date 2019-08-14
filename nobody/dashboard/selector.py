# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
"""
构图规划
DatePickerRange 时间范围
Dropdown        股票范围, 所有, 主板，中小板，创业版, 中证50, 沪深300
Dropdown        股价字段名: open, high, low, close
Slider          价格范围
Dropdown        股票形态: 长实体，吊颈线，十字星等。
Dropdown        技术指标: SMA, EMA, MACD, RSI, ATR, 唐奇安通道

DataTable       股票筛选结果, 包含字段: code, 行业, ohlc, atr, rsi
通过点击股票代码调转到股票行情

"""
import dash
import pandas as pd
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from os import path
from nobody.utils import get_ts_client
from nobody.utils import load_hist


external_stylesheets = ['https://cdn.bootcss.com/bootstrap/4.0.0/css/bootstrap.min.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(id="dash_app",
                      children=[
                              html.H1("This is Demo"),
                              html.H2("Plan"),
                              ],
                      style=main_style)


if __name__ == '__main__':
    app.run_server(debug=True)

