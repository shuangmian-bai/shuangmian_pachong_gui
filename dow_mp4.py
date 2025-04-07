import os
import shutil
import threading
import time
import requests
from requests.exceptions import RequestException, ConnectionError
import logging
from urllib3.exceptions import InsecureRequestWarning
from PyQt6.QtCore import pyqtSignal, QObject

# 手动创建日志文件并设置编码
log_file = 'dow_mp4.log'
with open(log_file, 'w', encoding='utf-8') as f:
    pass

# 配置日志记录器
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# 创建文件处理器并设置编码
file_handler = logging.FileHandler(log_file, encoding='utf-8')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# 将文件处理器添加到日志记录器
logger.addHandler(file_handler)


class DownloadProgress(QObject):
    progress_updated = pyqtSignal(int, int)  # 信号：发送已完成数量和总数


def retry_request(url, max_retries=3, backoff_factor=5):
    """尝试请求 URL，直到成功或达到最大重试次数"""
    session = requests.Session()
    retries = 0

    while retries < max_retries:
        try:
            response = session.get(url, timeout=10, verify=False)
            response.raise_for_status()  # 如果响应状态码不是 200，抛出异常
            return response
        except (ConnectionError, RequestException) as e:
            retries += 1
            if retries < max_retries:
                logging.error(f'请求失败: {url} (异常: {e}), 重试 {retries}/{max_retries}')
                time.sleep(backoff_factor)
            else:
                logging.error(f'请求失败: {url} (异常: {e}), 已达到最大重试次数')
                raise


def download_ts(ts_url, file_path, semaphore, failed_urls, progress_signal=None):
    """下载单个 ts 文件"""
    with semaphore:
        try:
            response = retry_request(ts_url)
            if response is None or len(response.content) == 0:
                raise Exception("Empty response")
            with open(file_path, 'wb') as f:
                f.write(response.content)
            logging.info(f'下载完成: {file_path}')
            if progress_signal:
                progress_signal.emit(progress_signal.receivers()[0][1] + 1, progress_signal.receivers()[0][2])
        except Exception as e:
            failed_urls.append(ts_url)
            logging.error(f'下载失败: {ts_url} (异常: {e})')
            if progress_signal:
                progress_signal.emit(progress_signal.receivers()[0][1], progress_signal.receivers()[0][2])


def download_ts_files(ts_list, output_dir, n, progress_signal=None):
    """下载所有 ts 文件"""
    semaphore = threading.Semaphore(n)
    failed_urls = []

    # 计算文件名长度
    lens = len(str(len(ts_list)))

    threads = []
    total_files = len(ts_list)
    completed_files = 0

    for i, ts in enumerate(ts_list):
        ts_name = str(i).zfill(lens)
        file_path = os.path.join(output_dir, f'{ts_name}.ts')

        # 检查文件是否存在
        if os.path.exists(file_path):
            completed_files += 1
            if progress_signal:
                progress_signal.emit(completed_files, total_files)
            continue

        # 创建线程对象
        t = threading.Thread(target=download_ts, args=(ts, file_path, semaphore, failed_urls, progress_signal))
        t.start()
        threads.append(t)

        # 每启动 n 个线程后等待 5 秒
        if (i + 1) % n == 0:
            time.sleep(5)

    # 等待所有线程完成
    for t in threads:
        t.join()

    return failed_urls


def concatenate_ts_files(output_dir, output_file):
    """合并 ts 文件"""
    ts_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('.ts')]
    ts_files.sort()  # 确保文件按顺序合并

    with open(output_file, 'wb') as outfile:
        for ts_file in ts_files:
            with open(ts_file, 'rb') as infile:
                outfile.write(infile.read())

    logging.info(f'文件合并完成: {output_file}')


def dow_mp4(ts_list, path, n, progress_signal=None):
    """主函数：下载并合并 TS 文件为 MP4"""
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    # 从参数中提取数据
    name = os.path.basename(path)
    base_path = os.path.dirname(path)
    output_dir_name = os.path.splitext(name)[0]  # 去掉扩展名
    output_dir = os.path.join(base_path, output_dir_name)
    output_file = os.path.join(base_path, name)

    # 确认路径存在
    os.makedirs(output_dir, exist_ok=True)

    # 检查输出文件是否已经存在
    if os.path.exists(output_file):
        logging.info(f'输出文件已存在: {output_file}')
        if progress_signal:
            progress_signal.emit(len(ts_list), len(ts_list))  # 设置进度条为100%
        return

    # 下载 ts 文件
    failed_urls = download_ts_files(ts_list, output_dir, n, progress_signal)

    # 检查下载结果
    if failed_urls:
        logging.error('\n以下文件下载失败:')
        for url in failed_urls:
            logging.error(url)
    else:
        logging.info('\n所有文件下载成功')
        # 合成 mp4 文件
        concatenate_ts_files(output_dir, output_file)
        # 删除 ts 文件
        shutil.rmtree(output_dir, ignore_errors=True)
