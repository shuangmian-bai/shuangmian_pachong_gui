import os
import shutil
import threading
import time  # 导入 time 模块
from utils import retry_request

# 定义锁对象
completed_files_lock = threading.Lock()

def download_ts(ts_url, file_path, semaphore, failed_urls, popup, task_name, completed_files, total_files, stop_flag):
    """下载单个 ts 文件"""
    with semaphore:
        try:
            while not stop_flag[0]:
                try:
                    response = retry_request(ts_url)
                    if response is None or len(response.content) == 0:
                        raise Exception("Empty response")
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    with completed_files_lock:
                        completed_files[0] += 1
                        print(completed_files[0])
                        popup.update_task_completed_amount(task_name, completed_files[0])  # 更新进度条
                    break
                except Exception as e:
                    failed_urls.append(ts_url)
                    time.sleep(5)  # 等待5秒后重试
        except Exception as e:
            failed_urls.append(ts_url)

def download_ts_files(ts_list, output_dir, n, popup, task_name, stop_flag):
    """下载所有 ts 文件"""
    semaphore = threading.Semaphore(n)
    failed_urls = []

    # 计算文件名长度
    lens = len(str(len(ts_list)))

    threads = []
    total_files = len(ts_list)
    completed_files = [0]  # 使用列表来存储共享变量
    update_interval = max(1, total_files // 10)  # 每下载 10% 的文件更新一次进度条

    for i, ts in enumerate(ts_list):
        ts_name = str(i).zfill(lens)
        file_path = os.path.join(output_dir, f'{ts_name}.ts')

        # 检查文件是否存在
        if os.path.exists(file_path):
            with completed_files_lock:
                completed_files[0] += 1
                if completed_files[0] % update_interval == 0:
                    popup.update_task_completed_amount(task_name, completed_files[0])
            continue

        # 创建线程对象
        t = threading.Thread(target=download_ts, args=(ts, file_path, semaphore, failed_urls, popup, task_name, completed_files, total_files, stop_flag))
        t.start()
        threads.append(t)

        # 每启动 n 个线程后等待 5 秒
        if (i + 1) % n == 0:
            time.sleep(5)

    # 等待所有线程完成
    for t in threads:
        t.join()

    # 更新最后一次进度条
    with completed_files_lock:
        popup.update_task_completed_amount(task_name, completed_files[0])

    return failed_urls

def concatenate_ts_files(output_dir, output_file):
    """合并 ts 文件"""
    # 检查输出目录是否存在并且包含 .ts 文件
    if not os.path.exists(output_dir):
        print(f"输出目录 {output_dir} 不存在")
        return

    ts_files = [os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('.ts')]
    if not ts_files:
        print(f"输出目录 {output_dir} 不包含任何 .ts 文件")
        return

    ts_files.sort()  # 确保文件按顺序合并

    # 使用 copy /b 命令合并 ts 文件，改为使用通配符 *.ts
    command = f'copy /b "{output_dir}\\*.ts" "{output_file}"'
    print(command)
    os.system(command)

def dow_mp4(ts_list, path, n, popup, task_name, stop_flag):
    """主函数：下载并合并 TS 文件为 MP4"""

    # 从参数中提取数据
    name = os.path.basename(path)
    base_path = os.path.dirname(path)
    output_dir_name = os.path.splitext(os.path.basename(path))[0]  # 去掉扩展名
    output_dir = os.path.join(os.path.dirname(path), output_dir_name)
    output_file = path

    # 确认路径存在
    os.makedirs(output_dir, exist_ok=True)

    # 检查输出文件是否已经存在
    if os.path.exists(output_file):
        popup.update_task_completed_amount(task_name, len(ts_list))
        return

    # 设置任务总量
    popup.set_task_amount(task_name, len(ts_list))

    # 下载 ts 文件
    failed_urls = download_ts_files(ts_list, output_dir, n, popup, task_name, stop_flag)

    # 检查下载结果
    if failed_urls:
        pass
    else:
        # 合成 mp4 文件
        concatenate_ts_files(output_dir, output_file)
        # 删除 ts 文件
        shutil.rmtree(output_dir, ignore_errors=True)