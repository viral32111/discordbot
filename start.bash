#!/bin/bash

set -e

docker run \
	--name discordbot \
	--hostname discordbot \
	--mount type=bind,source=/srv/discordbot/source,target=/srv/discordbot/source,readonly \
	--mount type=bind,source=/srv/discordbot/logs,target=/srv/discordbot/logs \
	--mount type=bind,source=/srv/discordbot/data,target=/srv/discordbot/data \
	--mount type=volume,source=relay,target=/var/run/relay \
	--workdir /srv/discordbot \
	--env-file secrets.env \
	--network host \
	--interactive \
	--tty \
	--restart unless-stopped \
	discordbot:local source/main.py
