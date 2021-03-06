import time


def log(*args, **kwargs):
    # time.time() 返回 unix time
    # 如何把 unix time 转换为普通人类可以看懂的格式呢？
    format = '%H:%M:%S'
    value = time.localtime(int(time.time()))
    # 1500057448 -> 7:38:38
    dt = time.strftime(format, value)
    print(dt, *args, **kwargs)
    # a append 追加模式
    with open('log.txt', 'a', encoding='utf-8') as f:
        print(dt, *args, file=f, **kwargs)
