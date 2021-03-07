#!/bin/bash

docker run \
	--name conspiracyai \
	--hostname conspiracyai \
	--read-only \
	--tmpfs /tmp/conspiracyai:rw,noexec,nosuid,nodev \
	--mount type=bind,source=/srv/conspiracy-ai/data,destination=/data \
	--mount type=bind,source=/srv/conspiracy-ai/source,destination=/data/source,readonly \
	--mount type=bind,source=/srv/conspiracy-ai/config,destination=/data/config,readonly \
	--mount type=bind,source=/srv/conspiracy-ai/.git/refs/heads/master,destination=/data/reference.txt,readonly \
	--mount type=bind,source=/var/run/docker.sock,destination=/var/run/docker.sock \
	--mount type=bind,source=/srv/minecraft/usercache.json,destination=/srv/minecraft/usercache.json,readonly \
	--mount type=bind,source=/srv/minecraft/minecraft.cid,destination=/srv/minecraft/minecraft.cid,readonly \
	--workdir /data \
	--env XDG_CACHE_HOME=/data/cache \
	--env PYTHONPATH=/data/packages \
	--network host \
	--interactive \
	--tty \
	--detach \
	--pull always \
	--restart unless-stopped \
	python:latest \
	/bin/bash -c 'pip install --no-input --no-color --progress-bar ascii --target packages --cache-dir cache --upgrade \
			git+https://github.com/Rapptz/discord.py \
			git+https://github.com/ytdl-org/youtube-dl \
			git+https://github.com/psf/requests \
			git+https://github.com/drgrib/dotmap \
			git+https://github.com/mysql/mysql-connector-python \
			git+https://github.com/Dinnerbone/mcstatus \
			git+https://github.com/msabramo/requests-unixsocket \
			python-dateutil \
			hurry.filesize \
			pytz \
			beautifulsoup4 \
			emoji && \
		python source/client.py'

docker attach conspiracyai
