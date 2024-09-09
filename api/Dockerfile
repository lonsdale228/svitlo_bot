FROM python:3.12.5-slim

WORKDIR /api

COPY requirements.txt /api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

COPY . /api

CMD ["python", "main.py"]