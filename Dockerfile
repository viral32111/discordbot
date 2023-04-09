# syntax=docker/dockerfile:1

# Start from my Node.js image
FROM ghcr.io/viral32111/nodejs:19-ubuntu

# Configuration
ARG DISCORD_BOT_DIRECTORY=/usr/local/discord-bot \
	DISCORD_BOT_DATA_DIRECTORY=/var/lib/discord-bot

# Copy the build artifact
COPY --chown=${USER_ID}:${USER_ID} . ${DISCORD_BOT_DIRECTORY}

# Create the data directory
RUN mkdir --verbose --parents ${DISCORD_BOT_DATA_DIRECTORY} && \
	chown --changes --recursive ${USER_ID}:${USER_ID} ${DISCORD_BOT_DATA_DIRECTORY}

# Switch to the regular user, in the data directory
USER ${USER_ID}:${USER_ID}
WORKDIR ${DISCORD_BOT_DATA_DIRECTORY}

# Persist the data directory
VOLUME ${DISCORD_BOT_DATA_DIRECTORY}

# Launch the bot
ENTRYPOINT [ "node", "/usr/local/bot" ]
