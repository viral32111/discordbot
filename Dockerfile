# docker build --pull --tag bot:latest .

FROM node:18-slim

ARG USER_ID=1000 \
	DIRECTORY_SOURCE=/usr/local/bot \
	DIRECTORY_DATA=/var/lib/bot

RUN mkdir --verbose --parents ${DIRECTORY_SOURCE}/source ${DIRECTORY_DATA} && \
	echo '{"main": "source/main.js", "type": "module"}' > ${DIRECTORY_SOURCE}/package.json && \
	chown --changes --recursive ${USER_ID}:${USER_ID} ${DIRECTORY_SOURCE} ${DIRECTORY_DATA}

COPY --chown=${USER_ID}:${USER_ID} emit/ ${DIRECTORY_SOURCE}/source

USER ${USER_ID}:${USER_ID}

WORKDIR ${DIRECTORY_DATA}
# VOLUME ${DIRECTORY_DATA}

ENTRYPOINT [ "node", "/usr/local/bot" ]
