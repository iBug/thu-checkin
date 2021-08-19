FROM python:3.9
WORKDIR /srv
RUN apt-get update && \
    apt-get install -y --no-install-recommends tesseract-ocr && \
    apt-get clean && \
    pip3 install requests pillow pytesseract
CMD ["python3", "checkin.py"]
