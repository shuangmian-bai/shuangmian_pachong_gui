import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

class MovieScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        self.base_url = 'https://www.bnjxjd.com'
        self.search_url = f'{self.base_url}/vodsearch.html'
        cache = self.search_url.replace('.html', '')
        self.search_page_url_template = f'{cache}/page/{{}}/wd/{{}}.html'

    def search_movies(self, query):
        try:
            req = requests.get(self.search_page_url_template.format(1, query), headers=self.headers)
            req.raise_for_status()  # 检查请求是否成功
            soup = BeautifulSoup(req.text, 'html.parser')

            # 尝试获取总页数
            try:
                page = soup.select('body > div:nth-child(1) > div > div > div.stui-pannel__ft > ul > li:nth-child(7) > a')[0].get(
                    'href').split('/')[3]
            except IndexError:
                page = 1

            url2_list = [self.search_page_url_template.format(i, query) for i in range(1, int(page) + 1)]

            # 使用多线程请求 url2_list
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(self.fetch_url, url) for url in url2_list]
                results = {}
                for future in futures:
                    try:
                        result = future.result()
                        results.update(self.process_result(result))
                    except Exception as e:
                        print(f"Error processing URL: {e}")

            return results

        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return {}

    def fetch_url(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Failed to fetch URL {url}: {e}")
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
                    print(f"Error parsing movie data: {e}")

            return re_data
        except Exception as e:
            print(f"Error processing result: {e}")
            return {}


if __name__ == '__main__':
    scraper = MovieScraper()
    datas = scraper.search_movies('哪吒')
