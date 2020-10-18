#!/bin/bash

/usr/bin/docker image pull python:latest

/usr/bin/docker run \
	--name conspiracyai \
	--hostname conspiracyai \
	--tmpfs /tmp:rw,noexec,nosuid,nodev \
	--mount type=bind,source=/srv/conspiracy-ai,destination=/usr/local/src/conspiracyai \
	--mount type=bind,source=/srv/conspiracy-ai/cache,destination=/var/tmp/conspiracyai \
	--workdir /usr/local/src/conspiracyai \
	--network host \
	--interactive \
	--tty \
	--detach \
	--restart unless-stopped \
	python:latest \
	/bin/bash -c 'XDG_CACHE_HOME=/var/tmp/conspiracyai pip install --upgrade --no-color --no-input pip wheel setuptools && \
		XDG_CACHE_HOME=/var/tmp/conspiracyai pip install --upgrade --no-color --no-input discord.py requests hurry.filesize mysql-connector-python pytz dotmap beautifulsoup4 youtube_dl && \
		python client.py'
