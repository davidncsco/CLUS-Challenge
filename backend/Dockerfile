FROM python:3.9.10-slim

COPY ./utils.py ./main.py ./database.py ./model.py /app/
COPY ./requirements.txt /app
COPY ./data /app/data

WORKDIR /app

RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host=0.0.0.0"]