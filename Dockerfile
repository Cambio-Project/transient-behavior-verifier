FROM ubuntu:20.04

WORKDIR /app

RUN apt-get update 

RUN apt-get install python3 -y
RUN apt-get upgrade python3-pip -y
RUN apt-get install python3-pip -y

COPY src/requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

RUN pip3 install bs4

COPY src /app

RUN sed -i 's/min_valdInf/min_val/g' ../usr/local/lib/python3.8/dist-packages/monitors/mtl.py

ENTRYPOINT [ "python3" ]

CMD ["main.py" ]
