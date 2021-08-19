#!/usr/bin/python3

import io
import os
import PIL
import pytesseract
import re
import requests

# https://stackoverflow.com/a/35504626/5958455
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


print("Tsinghua University Daily Health Report")

dirname = os.path.dirname(os.path.realpath(__file__))
data = {}
with open(os.path.join(dirname, "thu-checkin.txt"), "r") as f:
    for line in f:
        k, v = line.strip().split('=', 1)
        data[k] = v

username = data["USERNAME"]
password = data["PASSWORD"]
province = data['PROVINCE']
city = data["CITY"]
country = data["COUNTRY"]
is_inschool = data.get("IS_INSCHOOL", "2")

# 1: 在校园内, 2: 正常在家
now_status = "2" if is_inschool == "0" else "1"


CAS_LOGIN_URL = "https://passport.ustc.edu.cn/login"
CAS_CAPTCHA_URL = "https://passport.ustc.edu.cn/validatecode.jsp?type=login"
CAS_RETURN_URL = "https://weixine.ustc.edu.cn/2020/caslogin"
REPORT_URL = "https://weixine.ustc.edu.cn/2020/daliy_report"
# Not my fault:                                  ^^


retries = Retry(total=5,
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504])

s = requests.Session()
s.mount("https://", HTTPAdapter(max_retries=retries))
s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67"
r = s.get(CAS_LOGIN_URL, params={"service": CAS_RETURN_URL})
x = re.search(r"""<input.*?name="CAS_LT".*?>""", r.text).group(0)
cas_lt = re.search(r'value="(LT-\w*)"', x).group(1)

r = s.get(CAS_CAPTCHA_URL)
img = PIL.Image.open(io.BytesIO(r.content))
pix = img.load()
for i in range(img.size[0]):
    for j in range(img.size[1]):
        r, g, b = pix[i, j]
        if g >= 40 and r < 80:
            pix[i, j] = (0, 0, 0)
        else:
            pix[i, j] = (255, 255, 255)
lt_code = pytesseract.image_to_string(img).strip()

data = {
    "model": "uplogin.jsp",
    "service": CAS_RETURN_URL,
    "warn": "",
    "showCode": "1",
    "username": username,
    "password": password,
    "button": "",
    "CAS_LT": cas_lt,
    "LT": lt_code,
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
    "now_country": country,
    "gps_country": "",
    "now_detail": "",
    "body_condition": "1",
    "body_condition_detail": "",
    "now_status": now_status,
    "now_status_detail": "",
    "has_fever": "0",
    "last_touch_sars": "0",
    "last_touch_sars_date": "",
    "last_touch_sars_detail": "",
    "is_danger": "0",
    "is_goto_danger": "0",
    "jinji_lxr": "\uFFFD",
    "jinji_guanxi": "\uFFFD",
    "jiji_mobile": "\uFFFD",
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
