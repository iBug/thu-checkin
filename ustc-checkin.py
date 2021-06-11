#!/usr/bin/python3

import hashlib
import hmac
import json
import os
import re
import requests
import time

# https://stackoverflow.com/a/35504626/5958455
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


print("Tsinghua University Daily Health Report")

while True:
    try:
        requests.get("http://test6.ustc.edu.cn/", timeout=1)
    except requests.exceptions.ConnectionError:
        time.sleep(1)
    else:
        break

dirname = os.path.dirname(os.path.realpath(__file__))
data = {}
with open(os.path.join(dirname, "data.txt"), "r") as f:
    for line in f:
        k, v = line.strip().split('=', 1)
        data[k] = v

username = data["USERNAME"]
password = data["PASSWORD"]
province = data['PROVINCE']
city = data["CITY"]
is_inschool = data.get("IS_INSCHOOL", "2")

# 1: 在校园内, 2: 正常在家
now_status = "2" if is_inschool == "0" else "1"


CAS_LOGIN_URL = "https://passport.ustc.edu.cn/login"
CAS_RETURN_URL = "https://weixine.ustc.edu.cn/2020/caslogin"
REPORT_URL = "https://weixine.ustc.edu.cn/2020/daliy_report"
# Not my fault:                                  ^^
more_headers = {"Referer": "https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fweixine.ustc.edu.cn%2F2020%2Fcaslogin"}


retries = Retry(total=5,
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504])

s = requests.Session()
s.mount("https://", HTTPAdapter(max_retries=retries))
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
s.get(CAS_LOGIN_URL, params={"service": CAS_RETURN_URL})

data = {
    "model": "uplogin.jsp",
    "service": CAS_RETURN_URL,
    "warn": "",
    "showCode": "",
    "username": username,
    "password": password,
    "button": "",
}
r = s.post(CAS_LOGIN_URL, data=data, headers=more_headers)

# Parse the "_token" key out
x = re.search(r"""<input.*?name="_token".*?>""", r.text).group(0)
token = re.search(r'value="(\w*)"', x).group(1)

data = {
    "_token": token,
    "now_address": "1",
    "gps_now_address": "",
    "now_province": province,
    "gps_province": "",
    "now_city": city,
    "gps_city": "",
    "now_detail": "",
    "body_condition": "1",
    "body_condition_detail": "",
    "now_status": now_status,
    "now_status_detail": "",
    "has_fever": "0",
    "last_touch_sars": "0",
    "last_touch_sars_date": "",
    "last_touch_sars_detail": "",
    #"last_touch_hubei": "0",
    #"last_touch_hubei_date": "",
    #"last_touch_hubei_detail": "",
    #"last_cross_hubei": "0",
    #"last_cross_hubei_date": "",
    #"last_cross_hubei_detail": "",
    #"return_dest": "1",
    #"return_dest_detail": "",
    "other_detail": "\uFFFD",
    # https://twitter.com/tenderlove/status/722565868719177729
}

# Set "in_school" only when located in the right city
if province == "340000" and city == "340100":
    data["is_inschool"] = is_inschool

r = s.post(REPORT_URL, data=data, headers={"Referer": r.url})
with open(os.path.join(dirname, "last.html"), "wb") as f:
    f.write(r.content)

# Fail if not 200
r.raise_for_status()

if r.text.find("上报成功") >= 0:
    payload = json.dumps({"type": "checkin"})
else:
    payload = json.dumps({"type": "checkin-fail"})
signature = hmac.new(b"REDACTED", payload.encode("utf-8"), hashlib.sha1).hexdigest()
headers = {
    "Content-Type": "application/json",
    "X-GitHub-Event": "REDACTED",
    "X-Hub-Signature": f"sha1={signature}",
}
r = requests.post("https://www.example.com/", headers=headers, data=payload)
print(r)
print(r.text)
