#!/bin/bash
# Start script for jacpotflm- Bot

# Clone repo
if [ -z "$UPSTREAM_REPO" ]; then
    echo "Cloning main Repository"
    git clone https://github.com/skomar70/jacpotflm- /jacpotflm-
else
    echo "Cloning Custom Repo from $UPSTREAM_REPO"
    git clone "$UPSTREAM_REPO" /jacpotflm-
fi

# Go to project directory
cd /jacpotflm- || exit

# Install dependencies
pip3 install --no-cache-dir -U -r requirements.txt

# Start the bot
echo "Bot Started...."
python3 bot.py
