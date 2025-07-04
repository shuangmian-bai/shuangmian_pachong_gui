import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import logging
import traceback

logger = logging.getLogger(__name__)

class MovieScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        self.base_url = 'https://www.bnjxjd.com'
        self.search_url = f'{self.base_url}/vodsearch.html'
        cache = self.search_url.replace('.html', '')
        self.search_page_url_template = f'{cache}/page/{{}}/wd/{{}}.html'

    def fetch_and_process_url(self, url):
        """ 获取并处理 URL """
        try:
            response = self.fetch_url(url)
            if response:
                return self.process_result(response)
            else:
                return {}
        except Exception as e:
            logger.error(f"处理 URL {url} 时发生错误", exc_info=True)
            traceback.print_exc()
            return {}

    def search_movies(self, query):
        try:
            req = requests.get(self.search_page_url_template.format(1, query), headers=self.headers)
            req.raise_for_status()  # 检查请求是否成功
            soup = BeautifulSoup(req.text, 'html.parser')

            # 修复解析总页数的逻辑
            page_element = soup.select_one('body > div:nth-child(1) > div > div > div.stui-pannel__ft > ul > li:nth-last-child(2) > a')
            if page_element:
                page = page_element.get('href').split('/')[3]
            else:
                page = 1

            url2_list = [self.search_page_url_template.format(i, query) for i in range(1, int(page) + 1)]

            # 使用多线程请求 url2_list
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(self.fetch_and_process_url, url) for url in url2_list]
                results = {}
                for future in futures:
                    try:
                        result = future.result()
                        results.update(result)
                    except Exception as e:
                        logger.error(f"Error processing URL: {e}", exc_info=True)
                        traceback.print_exc()

            return results

        except requests.RequestException as e:
            logger.error(f"请求失败: {e}", exc_info=True)
            traceback.print_exc()
            return {}
        except Exception as e:
            logger.error("搜索电影时发生未知错误", exc_info=True)
            traceback.print_exc()
            return {}

    def fetch_url(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch URL {url}: {e}", exc_info=True)
            traceback.print_exc()
            return ""

    def process_result(self, result):
        re_data = {}

        try:
            soup = BeautifulSoup(result, 'html.parser')
            items = soup.select('.stui-vodlist.clearfix')
            if not items:
                return re_data

            movies = items[0].select('li')
            for movie in movies:
                try:
                    cache = movie.select('a')[0]
                    cache1 = cache.get('href')
                    cache2 = cache.get('title')
                    cache3 = movie.select('.pic-text1.text-right')[0].text
                    cache4 = movie.select('.pic-text.text-right')[0].text
                    text = f'{cache2}__{cache3}__{cache4}'
                    url = f'{self.base_url}{cache1}'
                    re_data[text] = url
                except (IndexError, AttributeError) as e:
                    logger.error(f"Error parsing movie data: {e}", exc_info=True)
                    traceback.print_exc()

            return re_data
        except Exception as e:
            logger.error(f"Error processing result: {e}", exc_info=True)
            traceback.print_exc()
            return {}

    def get_ji(self, url):
        try:
            req = requests.get(url, headers=self.headers)
            req.raise_for_status()
            soup = BeautifulSoup(req.text, 'html.parser')

            # 假设集数信息在 class 为 'stui-content__playlist' 的 div 中
            playlist = soup.select_one('.stui-content__playlist.clearfix')
            episodes = playlist.select('a')

            episode_data = {}
            for episode in episodes:
                path = self.base_url + episode.get('href')
                name = episode.text
                episode_data[name] = path
            return episode_data

        except requests.RequestException as e:
            logger.error(f"Request failed: {e}", exc_info=True)
            traceback.print_exc()
            return {}
        except Exception as e:
            logger.error(f"Error processing episode data: {e}", exc_info=True)
            traceback.print_exc()
            return {}

    def get_m3u8(self, url):
        """解析 m3u8 地址"""
        from m3u8_ts import get_m3u8
        return get_m3u8(self.headers, url)

    def get_ts_list(self, m3u8):
        from m3u8_ts import get_ts_list
        return get_ts_list(self.headers, m3u8)

    def dow_mp4(self, ts_list, path, n, progress_signal, task_name, stop_flag):
        from downloader import dow_mp4
        dow_mp4(ts_list, path, n, progress_signal, task_name, stop_flag)
