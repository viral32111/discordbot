# docker build --pull --file dockerfile tag viral32111/discordbot:latest /var/empty

FROM python:latest

ENV PYTHONDONTWRITEBYTECODE=TRUE

RUN pip install --upgrade pip && \
	pip install git+https://github.com/Rapptz/discord.py git+https://github.com/psf/requests git+https://github.com/mysql/mysql-connector-python git+https://github.com/ytdl-org/youtube-dl git+https://github.com/carpedm20/emoji git+https://github.com/fengsp/color-thief-py && \
	adduser --system --no-create-home --disabled-login --disabled-password --group --home /tmp --shell /usr/sbin/nologin --uid 1000 user

USER user:user

ENTRYPOINT [ "python" ]
CMD [ "--version" ]
