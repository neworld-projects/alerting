FROM python:3.10.6-buster

WORKDIR /usr/src/app
RUN apt update -y && apt install -y libsnappy-dev

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
CMD /bin/bash -c "/usr/src/app/run.sh"