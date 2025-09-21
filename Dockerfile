# Base Python image
FROM python:3.10-slim-bullseye

# System update + git install
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Workdir
WORKDIR /jacpotflm-

# Copy start.sh and make executable
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Logging
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["/bin/bash", "/start.sh"]
