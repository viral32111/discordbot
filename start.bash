#!/bin/bash

/usr/bin/docker image pull python:latest

/usr/bin/docker run \
	--name conspiracyai \
	--hostname conspiracyai \
	--tmpfs /tmp:rw,noexec,nosuid,nodev \
	--mount type=bind,source=/srv/conspiracy-ai/.git/refs/heads/master,destination=/tmp/conspiracyai/ref.txt,readonly \
	--mount type=bind,source=/srv/conspiracy-ai/source,destination=/usr/local/src/conspiracyai,readonly \
	--mount type=bind,source=/srv/conspiracy-ai/config,destination=/usr/local/etc/conspiracyai,readonly \
	--mount type=bind,source=/srv/conspiracy-ai/cache,destination=/var/tmp/conspiracyai \
	--mount type=bind,source=/srv/conspiracy-ai/data,destination=/var/lib/conspiracyai \
	--workdir /usr/local/src/conspiracyai \
	--env XDG_CACHE_HOME=/var/tmp/conspiracyai \
	--env PYTHONPYCACHEPREFIX=/var/tmp/conspiracyai/pycache \
	--network host \
	--interactive \
	--tty \
	--detach \
	--restart unless-stopped \
	python:latest \
	/bin/bash -c 'pip install --upgrade --no-color --no-input pip wheel setuptools && \
		pip install --upgrade --no-color --no-input discord.py requests hurry.filesize mysql-connector-python pytz dotmap beautifulsoup4 youtube_dl && \
		python client.py'
