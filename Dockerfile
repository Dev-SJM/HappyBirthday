FROM python:3.12

COPY . /app

RUN pip3 install flask boto3

WORKDIR /app

CMD [ "python3", "app.py" ]