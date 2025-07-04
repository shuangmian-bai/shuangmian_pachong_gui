import time
import requests
from bs4 import BeautifulSoup
import logging

def get_ts_list(head, m3u8):
    # 解析m3u8
    rel = requests.get(m3u8, headers=head)

    # 初始化返回列表
    ts_list = []

    logging.info(f'状态码为 : {rel.status_code}')

    if rel.status_code == 200:
        # 看看有没有子地址
        datas = rel.text.split('\n')
        m3u8 = m3u8[:m3u8.rfind('/') + 1]
        if len(datas) < 5:
            cache = [i for i, x in enumerate(datas) if x.find('.m3u8') != -1][0]
            cache = datas[cache]
            if cache[0:4] == 'http':
                m3u8 = cache
            else:
                m3u8 = m3u8 + cache

            logging.info('发现子m3u8等待10s后继续')
            logging.info(f'm3u8地址为 : {m3u8}')
            time.sleep(10)
            ts_list = get_ts_list(head, m3u8)
            return ts_list
        else:
            # 定义可能的后缀列表
            valid_extensions = ['.ts', '.mp4', '.m4s', '.jpeg']  # 根据实际情况添加或修改后缀
            a = 0
            for data in datas:
                if any(data.endswith(ext) for ext in valid_extensions):
                    if a == 0:
                        lens = len(data)
                        a += 1
                    if len(data) != lens:
                        continue
                    if data[0:4] == 'http':
                        ts = data
                    else:
                        ts = m3u8 + data
                    ts_list.append(ts)

            return ts_list

    # 如果错误直接返回空ts
    else:
        return []

def get_m3u8(head, url):
    """解析 m3u8 地址"""
    req = requests.get(url, headers=head)

    # 使用 BeautifulSoup 解析页面内容
    cache = req.text
    soup = BeautifulSoup(cache, 'html.parser')
    m3u8 = soup.select('.stui-player__video.embed-responsive.embed-responsive-16by9.clearfix')[0].select('script')[0].text
    m3u8 = m3u8.split(',"url":')[1]
    m3u8 = m3u8.split('"')[1]
    m3u8 = m3u8.replace(r'\/', '/')
    m3u8 = m3u8.encode('utf-8').decode('unicode_escape')

    # 检查是否有子 m3u8 地址
    req = requests.get(m3u8, headers=head)
    datas = req.text.split('\n')
    if len(datas) < 5:
        cache = [i for i, x in enumerate(datas) if x.find('.m3u8') != -1][0]
        cache = datas[cache]

        if cache.startswith('http'):
            m3u8 = cache
        else:
            m3u8 = m3u8[:m3u8.rfind('/') + 1] + cache

    return m3u8
