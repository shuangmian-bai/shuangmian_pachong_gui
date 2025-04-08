import os
import time
import requests
from requests.exceptions import RequestException, ConnectionError
from urllib3.exceptions import InsecureRequestWarning

# 忽略 InsecureRequestWarning 警告
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

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
                time.sleep(backoff_factor)
            else:
                raise

def process_path(dow_path):
    """处理路径字符串，确保路径合法且格式正确"""
    # 检查是否为相对路径
    is_relative = dow_path.startswith('./') or dow_path.startswith('../')

    # 处理 Windows 绝对路径中的冒号
    if os.name == 'nt' and ':' in dow_path:
        drive, path = dow_path.split(':', 1)
        path = path.lstrip('\\')  # 去除路径前的反斜杠
        dow_path = f"{drive}:{path}"

    # 替换非法字符
    illegal_chars = ['<', '>', '"', '|', '?', '*']
    for char in illegal_chars:
        dow_path = dow_path.replace(char, '_')  # 替换为单下划线更简洁

    # 使用 os.path 来处理路径分隔符
    dow_path = os.path.normpath(dow_path).replace(os.sep, '/')

    # 如果是相对路径，确保保留相对路径符号
    if is_relative and not dow_path.startswith('./'):
        dow_path = './' + dow_path

    # 确保路径末尾有且仅有一个斜杠
    if not dow_path.endswith('/'):
        dow_path += '/'

    return dow_path
