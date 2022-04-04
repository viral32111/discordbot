#!/bin/sh

docker run \
	--name discordbot \
	--hostname container \
	--memory 1024M \
	--mount type=volume,source=discordbot,target=/srv/discordbot/data \
	--mount type=bind,source=/srv/discordbot/source,target=/srv/discordbot/source,readonly \
	--mount type=bind,source=/srv/discordbot/logs,target=/srv/discordbot/logs \
	--workdir /srv/discordbot \
	--env-file secrets.env \
	--stop-signal SIGINT \
	--restart on-failure \
	--pull never \
	--detach \
	viral32111/discordbot:latest source/main.py
