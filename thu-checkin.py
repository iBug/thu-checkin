#!/usr/bin/python3

import atexit
import hashlib
import hmac
import json
import random
import threading
import time

import configparser
import datetime
import io
import mimetypes
import os
import PIL
import pytesseract
import re
import requests
import sys

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
reason = data["REASON"]
return_college = data["RETURN_COLLEGE"]
reason_text = data["REASON_TEXT"]
dorm_building = data["DORM_BUILDING"]
dorm = data["DORM"]

CAS_LOGIN_URL = "https://passport.ustc.edu.cn/login"
CAS_CAPTCHA_URL = "https://passport.ustc.edu.cn/validatecode.jsp?type=login"
CAS_RETURN_URL = "https://weixine.ustc.edu.cn/2020/caslogin"
HOME_URL = "https://weixine.ustc.edu.cn/2020/home"
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


def parse_token(s: str) -> str:
    x = re.search(r"""<input.*?name="_token".*?>""", s).group(0)
    return re.search(r'value="(\w*)"', x).group(1)


def make_session() -> requests.Session:
    retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67"
    return s


def login(s: requests.Session) -> requests.Response:
    r = s.get(CAS_LOGIN_URL, params={"service": CAS_RETURN_URL})
    cas_lt = re.search(r'<input.*?name="CAS_LT".*?value="(LT-\w*)".*?>', r.text).group(1)

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
    return s.post(CAS_LOGIN_URL, data=payload)


def checkin(s: requests.Session) -> bool:
    r = s.get(HOME_URL)
    payload = {
        "_token": parse_token(r.text),
        "juzhudi": "\uFFFD",
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
    with open("last.html", "wb") as f:
        f.write(r.content)

    # Fail if not 200
    r.raise_for_status()

    # Fail if not reported
    checkin_success = r.text.find("上报成功") >= 0
    return checkin_success


def apply(s: requests.Session) -> bool:
    r = s.get(WEEKLY_APPLY_URL)
    r = s.get(WEEKLY_APPLY_URL, params={"t": reason})
    now = datetime.datetime.now()
    start_date = now.strftime("%Y-%m-%d %H:%M:%S")
    end_date = (now + datetime.timedelta(days=int(now.hour > 20))).strftime("%Y-%m-%d 23:59:59")
    payload = {
        "_token": parse_token(r.text),
        "start_date": start_date,
        "end_date": end_date,
        "t": reason,
        "return_college[]": return_college.split(),
        "reason": reason_text,
    }
    r = s.post(WEEKLY_APPLY_POST_URL, data=payload)
    with open("last2.html", "wb") as f:
        f.write(r.content)

    # Fail if not applied
    apply_success = r.text.find("报备成功") >= 0
    return apply_success


def upload_image(s: requests.Session, idx: str, description: str) -> bool:
    path = data.get(f"IMAGE_{idx}")
    # Skip if not specified or not found
    if not path or not os.path.isfile(path):
        print(f"Skipping upload of {description}")
        return True
    print(f"Uploading {description}")
    with open(path, "rb") as f:
        blob = f.read()
        blob += os.urandom(1 + os.urandom(1)[0])
    r = s.get(UPLOAD_PAGE_URL)
    x = re.search(r"""<input.*?name="_token".*?>""", r.text).group(0)
    token = re.search(r'value="(\w*)"', x).group(1)
    url = UPLOAD_IMAGE_URL.format(idx)
    payload = {
        "_token": parse_token(r.text),
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
    upload_success = r.json()['status']
    print(f"Uploaded {description}: {upload_success}")
    return upload_success


def send_notification(t: str, content: object):
    payload = json.dumps({
        "type": t,
        "data": content,
    })
    print(f"Checkin result: {data}")
    signature = hmac.new(data["HMAC_SECRET"].encode(), payload.encode("utf-8"), hashlib.sha1).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": "stub",
        "X-Hub-Signature": f"sha1={signature}",
    }
    def notify(post_url, headers, payload):
        r = requests.post(post_url, headers=headers, data=payload, timeout=5)
        print("Notification:", r.status_code)
    th = threading.Thread(target=notify, args=(data["POST_URL"], headers, payload))
    th.start()
    atexit.register(th.join)


if __name__ == "__main__":
    s = make_session()
    results = [False] * 5
    try:
        login(s)
        results[0] = checkin(s)
        for idx, description in UPLOAD_INFO:
            results[2 + idx] = upload_image(s, idx, description)
        results[1] = apply(s)
        send_notification("checkin", results)
    except Exception:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.basename(exc_tb.tb_frame.f_code.co_filename)
        payload = {
            "message": f"{exc_type.__name__}: {exc_obj}",
            "file": fname,
            "lineno": exc_tb.tb_lineno,
        }
        send_notification("checkin-exception", payload)
