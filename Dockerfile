# Start from Node.js v18, running on Alpine
FROM node:18-alpine

# Configure directories & regular user's ID
ARG DISCORDBOT_DIRECTORY=/usr/local/bot \
	DISCORDBOT_DATA_DIRECTORY=/var/lib/bot \
	USER_ID=1000

# Create the directories & a basic NPM package file
RUN mkdir --verbose --parents ${DISCORDBOT_DIRECTORY}/source ${DISCORDBOT_DATA_DIRECTORY} && \
	echo '{"main": "./source/main.js", "type": "module"}' > ${DISCORDBOT_DIRECTORY}/package.json && \
	chown --changes --recursive ${USER_ID}:${USER_ID} ${DISCORDBOT_DIRECTORY} ${DISCORDBOT_DATA_DIRECTORY}

# Copy the JavaScript code into the image
COPY --chown=${USER_ID}:${USER_ID} ./ ${DISCORDBOT_DIRECTORY}/source

# Switch to the regular user, in the data directory
USER ${USER_ID}:${USER_ID}
WORKDIR ${DISCORDBOT_DATA_DIRECTORY}

# Persist the data directory
VOLUME ${DISCORDBOT_DATA_DIRECTORY}

# Start the bot on launch
ENTRYPOINT [ "node", "/usr/local/bot" ]
