FROM python:3.10

WORKDIR /app

COPY src/requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

RUN pip3 install bs4

COPY src /app

RUN sed -i 's/min_valdInf/min_val/g' ../usr/local/lib/python3.10/site-packages/monitors/mtl.py

ENV FLASK_APP=main.py

EXPOSE 5000

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
