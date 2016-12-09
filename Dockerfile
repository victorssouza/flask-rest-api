FROM python:3.3

COPY . /usr/src/app
WORKDIR /usr/src/app

RUN pip3 install -r requirements.txt

CMD ['/bin/sh']
