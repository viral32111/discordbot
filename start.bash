#!/bin/bash

docker run \
	--name conspiracy-ai \
	--tmpfs /tmp:noexec,nosuid,nodev,size=4G \
	--mount type=bind,source=/srv/conspiracy-ai/source,target=/srv/conspiracy-ai/source,readonly \
	--mount type=bind,source=/srv/conspiracy-ai/config,target=/srv/conspiracy-ai/config,readonly \
	--mount type=bind,source=/srv/conspiracy-ai/modules.txt,target=/srv/conspiracy-ai/modules.txt,readonly \
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
	bash -c 'pip install --requirement modules.txt && python source/client.py'

docker attach conspiracy-ai
