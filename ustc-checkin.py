#!/usr/bin/python3

import os
import re
import requests

# https://stackoverflow.com/a/35504626/5958455
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


print("Tsinghua University Daily Health Report")

dirname = os.path.dirname(os.path.realpath(__file__))
data = {}
with open(os.path.join(dirname, "ustc-checkin.txt"), "r") as f:
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
r = s.post(CAS_LOGIN_URL, data=data)

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
    "last_touch_hubei": "0",
    "last_touch_hubei_date": "",
    "last_touch_hubei_detail": "",
    "last_cross_hubei": "0",
    "last_cross_hubei_date": "",
    "last_cross_hubei_detail": "",
    "return_dest": "1",
    "return_dest_detail": "",
    "other_detail": "\uFFFD",
    # https://twitter.com/tenderlove/status/722565868719177729
}

# Set "in_school" only when located in the right city
if province == "340000" and city == "340100":
    data["is_inschool"] = is_inschool

r = s.post(REPORT_URL, data=data)

# Fail if not 200
r.raise_for_status()

# Fail if not reported
assert r.text.find("上报成功") >= 0
