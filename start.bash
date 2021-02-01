#!/bin/bash

/usr/bin/docker image pull python:latest

/usr/bin/docker run \
	--name conspiracyai \
	--hostname conspiracyai \
	--read-only \
	--tmpfs /tmp/conspiracyai:rw,noexec,nosuid,nodev \
	--mount type=bind,source=/srv/conspiracy-ai/data,destination=/data \
	--mount type=bind,source=/srv/conspiracy-ai/source,destination=/data/source,readonly \
	--mount type=bind,source=/srv/conspiracy-ai/config,destination=/data/config,readonly \
	--mount type=bind,source=/srv/conspiracy-ai/.git/refs/heads/master,destination=/data/reference.txt,readonly \
	--workdir /data \
	--env XDG_CACHE_HOME=/data/cache \
	--env PYTHONPATH=/data/packages \
	--network host \
	--interactive \
	--tty \
	--detach \
	--restart unless-stopped \
	python:latest \
	/bin/bash -c 'pip install --no-input --no-color --progress-bar ascii --target packages --cache-dir cache --upgrade \
			git+https://github.com/Rapptz/discord.py \
			git+https://github.com/ytdl-org/youtube-dl \
			git+https://github.com/psf/requests \
			git+https://github.com/drgrib/dotmap \
			git+https://github.com/mysql/mysql-connector-python \
			hurry.filesize \
			pytz \
			beautifulsoup4 \
			emoji && \
		python source/client.py'

/usr/bin/docker attach conspiracyai
