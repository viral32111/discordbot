###################################################################################
# Conspiracy AI - The official Discord bot for the Conspiracy Servers community.
# Copyright (C) 2016 - 2020 viral32111 (https://viral32111.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
###################################################################################

##############################################
# Setup this script
##############################################

# Import variables from the main script
from __main__ import chatCommands

# Import required modules
import discord, asyncio, time

##############################################
# Define chat commands
##############################################

# Sleep
@chatCommands( category = "Dev", wip = True )
async def sleep( message, arguments, client ):

	# Send a message if no arguments were provided
	if len( arguments ) < 1: return { "content": ":grey_exclamation: You must specify the duration to sleep for in seconds." }

	# Convert the duration argument to a float
	duration = float( arguments[ 0 ] )

	# Friendly message
	await message.channel.send( "Sleeping for `" + "{0:.16f}".format( duration ) + "` seconds..." )

	# Store high resolution time in seconds of when the sleeping started
	started = time.perf_counter()

	# Sleep
	await asyncio.sleep( duration )

	# Store high resolution time in seconds of when the sleeping finished
	finished = time.perf_counter() - started

	# Friendly message
	await message.channel.send( "Finished sleeping, sleep lasted exactly `" + "{0:.16f}".format( finished ) + "` seconds." )
