import os
from utils import log
import requests
from pyquery import PyQuery as pq

"""
时光网TOP100爬虫

这个爬虫可以爬 10 个页面, 把所有 TOP100 电影都爬出来
并且加入了缓存页面功能
不用重复请求了(网络请求很 浪费时间)
这样做有两个好处
    1, 增加新内容(比如增加评论人数)的时候不用重复请求网络
    2, 出错的时候有原始数据对照

把封面给下载下来 并保存在image文件夹中
"""


class Model(object):
    def __repr__(self):
        name = self.__class__.__name__
        properties = ('{}=({})'.format(k, v) for k, v in self.__dict__.items())
        s = '\n<{} \n  {}>'.format(name, '\n  '.join(properties))
        return s


class Movie(Model):
    def __init__(self):
        self.name = ''
        self.score = 0
        self.quote = ''
        self.cover_url = ''
        self.ranking = 0


def cached_url(url):
    """
    缓存, 避免重复下载网页浪费时间
    """
    folder = 'cached'

    if '-' in url:
        filename = url.split('-', 1)[-1]
    else:
        filename = '1.html'

    path = os.path.join(folder, filename)
    if os.path.exists(path):
        with open(path, 'rb') as f:
            s = f.read()
        return s
    else:
        # 建立 cached 文件夹
        if not os.path.exists(folder):
            os.makedirs(folder)
        # 发送网络请求, 把结果写入到文件夹中
        r = requests.get(url)
        with open(path, 'wb') as f:
            f.write(r.content)
        return r.content


def movie_from_div(ranking, name, score, quote, cover_url):
    """
    从 div 里面获取到一个电影信息
        div1 = ranking[i]
        div2 = name[i]
        div3 = score[i]
        div4 = quote[i]
        div5 = cover_url[i]

    """
    e_ranking = pq(ranking)
    e_name = pq(name)
    e_score = pq(score)
    e_quote = pq(quote)
    e_cover = pq(cover_url)

    # 小作用域变量用单字符
    m = Movie()
    # 排名序号
    m.ranking = e_ranking('.number em').text()
    log('m.ranking', m.ranking)
    # 电影名字：前三名和后面标签不同
    if int(m.ranking) > 3:
        name = e_name('.c_blue').text()
        m.name = name.split(')', 1)[0]
    else:
        name = e_name('.c_fff').text()
        m.name = name.split(')', 1)[0]
    # point 评分分为两部分
    m.score = e_score('.total').text() + e_score('.total2').text()
    # 简介
    m.quote = e_quote('.mt3').text()
    # 图片链接
    m.cover_url = e_cover('img').attr('src')
    return m


def download_image(url, filename):
    r = requests.get(url)

    folder = 'image'
    if not os.path.exists(folder):
        os.makedirs(folder)
    path = os.path.join(folder, filename)

    with open(path, 'wb') as f:
        f.write(r.content)


def save_cover(movies):
    for m in movies:
        filename = '{}.jpg'.format(m.ranking)
        download_image(m.cover_url, filename)


def movies_from_url(url):
    page = cached_url(url)
    e = pq(page)

    ranking = e('.number')
    name = e('.mov_con')
    score = e('.mov_point')
    quote = e('.mt3')
    cover_url = e('img')

    movies = []
    for i in range(0, len(name)):
        # 调用 movie_from_div
        div1 = ranking[i]
        div2 = name[i]
        div3 = score[i]
        div4 = quote[i]
        div5 = cover_url[i]
        movie = movie_from_div(div1, div2, div3, div4, div5)
        movies.append(movie)
    return movies


def main():
    for i in range(1, 11):
        if i < 2:
            url = "http://www.mtime.com/top/movie/top100/"
        else:
            url = "http://www.mtime.com/top/movie/top100/index-{}.html".format(i)
        movies = movies_from_url(url)
        log('top100 movies', movies)
        save_cover(movies)


if __name__ == '__main__':
    main()
