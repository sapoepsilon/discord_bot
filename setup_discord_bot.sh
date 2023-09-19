#!/bin/bash

# Install Python3 and pip
sudo apt update
sudo apt install -y python3 python3-pip

# Install Python packages
pip3 install discord.py

# Create a directory to store the bot
mkdir -p ~/Developer/discord_bot
cd ~/Developer/discord_bot

# Create the bot Python script
cat << 'EOF' > discord_bot.py
# Your Python code here
EOF

# Paste your bot code inside the 'EOF' and 'EOF' tags in the above section

# Create a systemd service file for the bot
cat << EOF | sudo tee /etc/systemd/system/discord_bot.service > /dev/null
[Unit]
Description=Discord Bot Service
After=multi-user.target

[Service]
WorkingDirectory=/home/$USER/Developer/discord_bot
ExecStart=/usr/bin/python3 /home/$USER/Developer/discord_bot/discord_bot.py
Restart=always
User=$USER

[Install]
WantedBy=multi-user.target
EOF

# Reload the systemd daemon
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable discord_bot.service
sudo systemctl start discord_bot.service
