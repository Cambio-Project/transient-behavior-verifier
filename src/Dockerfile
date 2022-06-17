FROM ubuntu:20.04

WORKDIR /app

RUN apt-get update 

RUN apt-get install python3 -y
RUN apt-get upgrade python3-pip -y
RUN apt-get install python3-pip -y

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

RUN pip3 install bs4

COPY . /app

ENTRYPOINT [ "python3" ]

CMD ["main.py" ]