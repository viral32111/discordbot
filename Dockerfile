# Use the latest Python image as a base
FROM python:latest

# Set the current version of the bot in the environment
ENV VERSION=3.0.0

# Use a keyboard interrupt signal for stopping this image
STOPSIGNAL SIGINT

# Install all dependencies through pip
RUN pip install git+https://github.com/Rapptz/discord.py git+https://github.com/ytdl-org/youtube-dl git+https://github.com/psf/requests git+https://github.com/mysql/mysql-connector-python git+https://github.com/Dinnerbone/mcstatus git+https://github.com/msabramo/requests-unixsocket git+https://github.com/viral32111/slashcommands python-dateutil hurry.filesize pytz beautifulsoup4 emoji

# Include the configuration files and source code directories
COPY config /usr/local/discordbot/etc
COPY source /usr/local/discordbot/src

# Set the working directory to where the configuration files and source code is
WORKDIR /usr/local/discordbot

# Set the default command to execute the main source code script
ENTRYPOINT python src/client.py
