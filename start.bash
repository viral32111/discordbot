#!/bin/bash

set -e

if [ "$1" = "dev" ]; then
	docker run \
		--name conspiracy-ai \
		--tmpfs /tmp:noexec,nosuid,nodev,size=4G \
		--mount type=bind,source=/srv/conspiracy-ai/source,target=/srv/conspiracy-ai/source,readonly \
		--mount type=bind,source=/srv/conspiracy-ai/config,target=/srv/conspiracy-ai/config,readonly \
		--mount type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock \
		--mount type=bind,source=/home/viral32111/slashcommands,target=/slashcommands \
		--workdir /srv/conspiracy-ai \
		--env-file secrets.conf \
		--env LOCAL_COMMIT_REFERENCE=$(cat /srv/conspiracy-ai/.git/refs/heads/main) \
		--network host \
		--tty \
		--interactive \
		--rm \
		--pull always \
		python:latest \
		bash -c 'pip install \
			git+https://github.com/Rapptz/discord.py \
			git+https://github.com/ytdl-org/youtube-dl \
			git+https://github.com/psf/requests \
			git+https://github.com/mysql/mysql-connector-python \
			git+https://github.com/Dinnerbone/mcstatus \
			git+https://github.com/msabramo/requests-unixsocket \
			python-dateutil \
			hurry.filesize \
			pytz \
			beautifulsoup4 \
			emoji && \
			pip install --editable /slashcommands && \
			bash'
else
	docker run \
		--name conspiracy-ai \
		--tmpfs /tmp:noexec,nosuid,nodev,size=4G \
		--mount type=bind,source=/srv/conspiracy-ai/source,target=/srv/conspiracy-ai/source,readonly \
		--mount type=bind,source=/srv/conspiracy-ai/config,target=/srv/conspiracy-ai/config,readonly \
		--mount type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock \
		--workdir /srv/conspiracy-ai \
		--env-file secrets.conf \
		--env LOCAL_COMMIT_REFERENCE=$(cat /srv/conspiracy-ai/.git/refs/heads/main) \
		--network host \
		--tty \
		--interactive \
		--restart unless-stopped \
		--detach \
		--pull always \
		python:latest \
		bash -c 'pip install \
			git+https://github.com/Rapptz/discord.py \
			git+https://github.com/ytdl-org/youtube-dl \
			git+https://github.com/psf/requests \
			git+https://github.com/mysql/mysql-connector-python \
			git+https://github.com/Dinnerbone/mcstatus \
			git+https://github.com/msabramo/requests-unixsocket \
			git+https://github.com/viral32111/slashcommands \
			python-dateutil \
			hurry.filesize \
			pytz \
			beautifulsoup4 \
			emoji && \
			python source/client.py'

	docker attach conspiracy-ai
fi
