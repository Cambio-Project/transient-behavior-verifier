FROM python:3.10

WORKDIR /app

COPY src/requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

RUN pip3 install bs4

COPY src /app

ENV FLASK_APP=main.py

EXPOSE 5000

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
