FROM python:3.11-rc-bullseye

COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt

COPY *.py /usr/src/app/
COPY templates/status.html /usr/src/app/templates/
COPY static/* /usr/src/app/static/

EXPOSE 5000

CMD ["python3", "/usr/src/app/device.py"]