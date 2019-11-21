def sma(shuju,N,M):
    where_are_nan = np.isnan(shuju)
    shuju[where_are_nan] = 0
    a = [shuju[0]]
    for i in range(1,len(shuju)):
        sma = (shuju[i]*float(M) + a[i-1]*(N-1))/N
        a.append(sma)
    return np.array(a)


def get_kdj(high, low, close, n, m1, m2):
    llow = low.rolling(n).min()
    hhigh = high.rolling(n).max()
    rsv = ((close - llow) / (hhigh - llow)) * 100
    # K = rsv.ewm(span=m1).mean()
    # D = K.ewm(span=m2).mean()
    # K = rsv.rolling(m1).mean()
    # D = K.rolling(m2).mean()
    K = sma(rsv, m1, 1)
    D = sma(K, m2, 1)
    J = 3 * K - 2 * D

    return K, D, J
