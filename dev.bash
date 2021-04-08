#!/bin/bash

# Create image: docker build -t conspiracy-ai:dev .

docker run \
	--name conspiracy-ai \
	--mount type=bind,source=$(pwd)/config,target=/usr/local/discordbot/etc,readonly \
	--mount type=bind,source=$(pwd)/source,target=/usr/local/discordbot/src,readonly \
	--mount type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock \
	--env-file secrets.conf \
	--interactive \
	--tty \
	--rm \
	conspiracy-ai:dev
