FROM python:3.9
WORKDIR /srv
RUN pip3 install requests
ADD checkin.py ./
CMD ["python3", "checkin.py"]
