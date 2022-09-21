FROM python:3.8-alpine3.15

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

RUN python3 -m nltk.downloader punkt

COPY . .

EXPOSE 5000
CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0" ]
