# docker build -t discordbot:local -f dockerfile /tmp/empty

FROM python:latest

RUN apt-get update && apt-get upgrade --yes && pip install --upgrade pip

RUN pip install git+https://github.com/Rapptz/discord.py git+https://github.com/psf/requests git+https://github.com/mysql/mysql-connector-python git+https://github.com/ytdl-org/youtube-dl

RUN adduser --system --no-create-home --disabled-login --disabled-password --group --home / --shell /usr/sbin/nologin --uid 2005 discordbot
USER discordbot:discordbot

ENTRYPOINT [ "python" ]
CMD [ "--version" ]
