#!/usr/bin/python3

import configparser
import datetime
import io
import mimetypes
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
config = configparser.ConfigParser()
config.read(os.path.join(dirname, "thu-checkin.txt"))
data = config["thu-checkin"]

username = data["USERNAME"]
password = data["PASSWORD"]
juzhudi = data["JUZHUDI"]
reason = data["REASON"]
return_college = data["RETURN_COLLEGE"]
dorm_building = data["DORM_BUILDING"]
dorm = data["DORM"]

CAS_LOGIN_URL = "https://passport.ustc.edu.cn/login"
CAS_CAPTCHA_URL = "https://passport.ustc.edu.cn/validatecode.jsp?type=login"
CAS_RETURN_URL = "https://weixine.ustc.edu.cn/2020/caslogin"
REPORT_URL = "https://weixine.ustc.edu.cn/2020/daliy_report"
# Not my fault:                                  ^^
WEEKLY_APPLY_URL = "https://weixine.ustc.edu.cn/2020/apply/daliy"
WEEKLY_APPLY_POST_URL = "https://weixine.ustc.edu.cn/2020/apply/daliy/post"

UPLOAD_PAGE_URL = "https://weixine.ustc.edu.cn/2020/upload/xcm"
UPLOAD_IMAGE_URL = "https://weixine.ustc.edu.cn/2020/upload/{}/image"
UPLOAD_INFO = [
    (1, "14-day Big Data Trace Card"),
    (2, "An Kang code"),
    (3, "Weekly nucleic acid test result"),
]


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

payload = {
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
r = s.post(CAS_LOGIN_URL, data=payload)

# Parse the "_token" key out
x = re.search(r"""<input.*?name="_token".*?>""", r.text).group(0)
token = re.search(r'value="(\w*)"', x).group(1)

payload = {
    "_token": token,
    "juzhudi": juzhudi,
    "dorm_building": dorm_building,
    "dorm": dorm,
    "body_condition": "1",
    "body_condition_detail": "",
    "now_status": "1",
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

r = s.post(REPORT_URL, data=payload)

# Fail if not 200
r.raise_for_status()

# Fail if not reported
assert r.text.find("上报成功") >= 0


# Now apply for outgoing
r = s.get(WEEKLY_APPLY_URL)
r = s.get(WEEKLY_APPLY_URL, params={"t": reason})
x = re.search(r"""<input.*?name="_token".*?>""", r.text).group(0)
token = re.search(r'value="(\w*)"', x).group(1)
now = datetime.datetime.now()
start_date = now.strftime("%Y-%m-%d %H:%M:%S")
end_date = (now + datetime.timedelta(days=0)).strftime("%Y-%m-%d 23:59:59")
payload = {
    "_token": token,
    "start_date": start_date,
    "end_date": end_date,
    "t": reason,
    "return_college[]": return_college.split(),
}
r = s.post(WEEKLY_APPLY_POST_URL, data=payload)

# Fail if not applied
assert r.text.find("报备成功") >= 0


# Now upload images
for idx, description in UPLOAD_INFO:
    path = data.get(f"IMAGE_{idx}")
    # Skip if not specified or not found
    if not path or not os.path.isfile(path):
        print(f"Skipping upload of {description}")
        continue
    print(f"Uploading {description}")
    with open(path, "rb") as f:
        blob = f.read()
    r = s.get(UPLOAD_PAGE_URL)
    x = re.search(r"""<input.*?name="_token".*?>""", r.text).group(0)
    token = re.search(r'value="(\w*)"', x).group(1)
    url = UPLOAD_IMAGE_URL.format(idx)
    payload = {
        "_token": token,
        "id": f"WU_FILE_{idx}",
        "name": os.path.basename(path),
        "type": mimetypes.guess_type(path)[0],
        "lastModifiedDate": datetime.datetime.now()
            .strftime("%a %b %d %Y %H:%M:%S GMT+0800 (China Standard Time)"),
        "size": f"{len(blob)}",
    }
    payload_files = {"file": (payload["name"], blob)}
    r = s.post(url, data=payload, files=payload_files)
    r.raise_for_status()
    print(f"Uploaded {description}: {r.json()['status']}")
