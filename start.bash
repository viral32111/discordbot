#!/bin/bash

set -e

docker run \
	--name discordbot \
	--hostname discordbot \
	--mount type=bind,source=/srv/discordbot/source,target=/srv/discordbot,readonly \
	--workdir /srv/discordbot \
	--env-file secrets.env \
	--network host \
	--interactive \
	--tty \
	--rm \
	discordbot:local client.py
