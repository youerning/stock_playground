import pandas as pd
from os import path
from glob import glob
from datetime import datetime
# import talib


data_path = path.join("data", "stock")
code_file_lst = glob(path.join(data_path, "*csv"))
global_ma_lst = [5, 20, 60, 120]
gloabl_ma_cols = ["ma%s" % i for i in global_ma_lst]
# cached_ma_lst = []
global_stk_lst = []

for fp in code_file_lst:
    stk = pd.read_csv(fp)
    if len(stk) > max(global_ma_lst):
        global_stk_lst.append(stk)
        stk["code"] = path.basename(fp)
    
    for ma in global_ma_lst:
        name = "ma%s" % ma
        if len(stk) >= ma:
            stk[name] = stk.close.rolling(ma).mean()
    stk.dropna(inplace=True)

    
def dense_detector(ser, ratio=0.0025):
    max_ = max(ser.values)
    min_ = min(ser.values)
    if ((max_ - min_) / max_) < ratio:
        return 1
    return 0


def find_dense():
    dense_ret = pd.DataFrame()
    print("stock size: %s" % len(global_stk_lst))
    count = 0
    for stk in global_stk_lst:
        stk["dense"] = stk[gloabl_ma_cols].apply(dense_detector, axis=1)
        ret = stk[stk.dense > 0]

        if len(ret) > 0:
            count += 1
            dense_ret = dense_ret.append(ret)
    # print(ret)
    # print(len(dense_ret))
    print("dense count: %s" % count) 
    dense_ret.to_csv("dense.csv", index=False)


def main():
    pass

if __name__ == "__main__":
    print("start at: %s" % str(datetime.now()))
    find_dense()
    print("end at: %s" % str(datetime.now()))
    print("finished")