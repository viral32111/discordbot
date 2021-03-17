#!/bin/bash

docker run \
	--name conspiracy-ai \
	--tmpfs /tmp:noexec,nosuid,nodev,size=4G \
	--mount type=bind,source=/srv/conspiracy-ai/source,target=/srv/conspiracy-ai/source,readonly \
	--mount type=bind,source=/srv/conspiracy-ai/config,target=/srv/conspiracy-ai/config,readonly \
	--mount type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock \
	--workdir /srv/conspiracy-ai \
	--env LOCAL_COMMIT_REFERENCE=$(cat /srv/conspiracy-ai/.git/refs/heads/master) \
	--network host \
	--tty \
	--interactive \
	--detach \
	--restart unless-stopped \
	--pull always \
	python:latest \
	bash -c 'pip install \
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

docker attach conspiracy-ai
