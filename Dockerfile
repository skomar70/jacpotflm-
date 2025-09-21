# Base Python image
FROM python:3.10.8-slim-buster

# System update + git install
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Workdir
RUN mkdir /jacpotflm-
WORKDIR /jacpotflm-

# Copy requirements and install
COPY requirements.txt /requirements.txt
RUN pip3 install --no-cache-dir -U pip && \
    pip3 install --no-cache-dir -r requirements.txt

# Copy start.sh and make executable
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Logging
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["/bin/bash", "/start.sh"]
