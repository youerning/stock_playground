# -*- coding: utf-8 -*-
# @Author: youerning
# @Email: 673125641@qq.com
from pytdx.hq import TdxHq_API
from pytdx.params import TDXParams
from pytdx.config.hosts import hq_hosts
import os
import json
import random
import traceback
from multiprocessing import Manager
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import wait
from os import path

# cur_dir = path.abspath(path.dirname(__file__))
stock_data_path = path.join("data", "tdx", "stock")
index_data_path = path.join("data", "tdx", "index")
hy_cache_path = "hy_cache.json"
# api = TdxHq_API(heartbeat=True, auto_retry=True, multithread=True)
ktype = TDXParams.KLINE_TYPE_1HOUR
# host = '119.147.212.81'
# port = 7709
years = 3

# stock
tdxhy_path = "tdxhy.cfg"
# index
tdxzs_path = "tdxzs.cfg"
# 进程数量
process_pool_size = 4
# wheter to overwrite old data
overwrite = False

def get_hy(zs_fp, hy_fp):
    if path.exists(hy_cache_path):
        with open(hy_cache_path, encoding="utf8") as rf:
            return json.load(rf)
    zs_map = {}
    with open(zs_fp, encoding="utf8") as rf:
        for line in rf:
            name, code, _, market, _, hy_code = line.split("|")
            zs_map[hy_code.strip()] = dict(name=name, code=code, market=market)
    
    hy_map = {}
    with open(hy_fp, encoding="utf8") as rf:
        for line in rf:
            market, code, hy_code, _ = line.split("|", maxsplit=3)
            if hy_code in zs_map:
                if hy_code not in hy_map:
                    hy_map[hy_code] = zs_map[hy_code]
                    hy_map[hy_code]["stock"] = [dict(market=market, code=code)]
                    continue
                hy_map[hy_code]["stock"].append(dict(market=market, code=code))
        
    
    with open(hy_cache_path, "w", encoding="utf8") as wf:
        json.dump(hy_map, wf, indent=4, default=str, ensure_ascii=False)
    return hy_map

def download(api, market, code, start, count=800, isindex=False):
    if isindex:
        fp = path.join(index_data_path, "%s.csv" % code)
        if path.exists(fp) and not overwrite:
            print("指数 %s|%s 已存在" % (market, code))
            return
        
        data = []
        for i in range(years):
            new_data = api.get_index_bars(ktype, int(market), code, (years - i - 1) * count, count)
            if new_data:
                data += new_data
        
        if data:
            api.to_df(data).to_csv(fp, index=False)
            print("下载指数 %s|%s 成功" % (market, code))
        else:
            print("下载指数 %s|%s 失败" % (market, code))
    else:
        fp = path.join(stock_data_path, "%s.csv" % code)
        if path.exists(fp) and not overwrite:
            print("股票 %s|%s 已存在" % (market, code))
            return
        data = []
        for i in range(years):
            new_data = api.get_security_bars(ktype, int(market), code, (years - i - 1) * count, count)
            if new_data:
                data += new_data
        
        if data:
            api.to_df(data).to_csv(fp, index=False)
            print("下载股票 %s|%s 成功" % (market, code))
        else:
            print("下载股票 %s|%s 失败" % (market, code))

def div_lst(lst, shares):
    min_size = len(lst) // shares
    if min_size == 0:
        raise
    ret = []
    for i in range(shares):
        item = lst[min_size * i: (i+1) * min_size]
        ret.append(item)
    if min_size * shares < len(lst):
        item = lst[min_size * shares: len(lst)]
        ret.append(item)
    return ret

def worker(q, hy_map, hy_code):
    index_market, index_code = hy_map[hy_code]["market"], hy_map[hy_code]["code"]
    stock_lst = hy_map[hy_code]["stock"]
    download_lst = [dict(market=index_market, code=index_code, index=True)]
    download_lst.extend(stock_lst)
    
    # 下载指数 historical data
    try:
        server_addr = q.get(timeout=2)
    except Exception as e:
        print("没有可用的服务器")
        return
    api = TdxHq_API(heartbeat=True, auto_retry=True, multithread=True)
    try:
        if api.connect(*server_addr[1:]):
            for item in download_lst:
                market = item["market"]
                code = item["code"]
                isindex = item.get("index", False)
                download(api, market, code, years, isindex=isindex)
    except Exception as e:
        print(e)
        traceback.print_exc()
        print("进程下载失败")
    finally:
        api.disconnect()
    q.put(server_addr)
    return

def main():
    manager = Manager()
    q = manager.Queue()
    if not path.exists(stock_data_path):
        os.makedirs(stock_data_path)
    
    if not path.exists(index_data_path):
        os.makedirs(index_data_path)
    
    hy_map = get_hy(tdxzs_path, tdxhy_path)
    print("总共行业数量: %s" % len(hy_map))
    pool = ProcessPoolExecutor(process_pool_size)
    api = TdxHq_API(heartbeat=True, auto_retry=True, multithread=True)
    print("寻找可用服务器...")
    server_count = 0
    for data_server in random.choices(hq_hosts, k=4):
        try:
            if api.connect(*data_server[1:]):
                q.put(data_server)
                server_count += 1
        except Exception:
            print("连接服务器失败")
        finally:
            api.disconnect()

    print("可用服务器: %s" % server_count)
    if server_count < 1:
        print("没有可用服务器")
    print("开始下载数据...")
    fut_lst = []
    for hy_code in hy_map:
        fut_lst.append(pool.submit(worker, q, hy_map, hy_code))
    # print(len(fut_lst))
    wait(fut_lst)
    print(fut_lst[0].result())
def test():
    pass
if __name__ == '__main__':
    main()
