FROM python:3.10
WORKDIR /srv
ENV DEBIAN_FRONTEND=noninteractive TZ=Asia/Shanghai
RUN sed -Ei 's/(deb|security)\.debian\.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends tesseract-ocr && \
    apt-get clean && \
    ln -sfn /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure tzdata && \
    pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip3 install requests pillow pytesseract
CMD ["python3", "thu-checkin.py"]
