FROM python:3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY picflip64.py .

ENTRYPOINT [ "python", "./picflip64.py" ]