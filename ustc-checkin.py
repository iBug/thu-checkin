#!/usr/bin/python3

import os
import re
import requests

s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
s.get("https://passport.ustc.edu.cn/login", params={"service": "https://weixine.ustc.edu.cn/2020/caslogin"})

# Send CAS credentials
r = s.post("https://passport.ustc.edu.cn/login", data={
    "model": "uplogin.jsp",
    "service": "https://weixine.ustc.edu.cn/2020/caslogin",
    "warn": "",
    "showCode": "",
    "username": os.environ["USERNAME"],
    "password": os.environ["PASSWORD"],
    "button": "",
})

# Parse the "_token" key out
x = re.search(r"""<input.*?name="_token".*?>""", r.text)
token = re.search(r'value="(\w*)"', x[0])[1]
r = s.post("https://weixine.ustc.edu.cn/2020/daliy_report", data={
    "_token": token,
    "now_address": "1",
    "gps_now_address": "",
    "now_province": os.environ["PROVINCE"],
    "gps_province": "",
    "now_city": os.environ["CITY"],
    "gps_city": "",
    "now_detail": "",
    "body_condition": "1",
    "body_condition_detail": "",
    "now_status": "2",
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
})

# Fail if not 200
r.raise_for_status()
