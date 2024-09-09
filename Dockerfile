FROM python:3.12.2-slim

WORKDIR /bot

COPY requirements.txt /bot/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /bot/requirements.txt

COPY . /bot

CMD ["python", "bot.py"]