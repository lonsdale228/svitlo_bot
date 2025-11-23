FROM python:3.12.2-slim

WORKDIR /bot

RUN apt-get update && apt-get install -y --no-install-recommends \
    wkhtmltopdf \
    xvfb \
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    libfreetype6 \
    libpng16-16 \
    libjpeg62-turbo \
    libssl3 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /bot/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /bot/requirements.txt

COPY . /bot

CMD ["python", "bot.py"]
