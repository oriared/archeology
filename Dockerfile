FROM python

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app app
COPY runner.py runner.py

COPY config.toml config.toml

ENV FLASK_APP=runner.py

ENTRYPOINT flask db init && flask db migrate && flask db upgrade && flask run -h 0.0.0.0
